#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import requests
from time import sleep
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
sslverify = False

SPLUNK_URL='https://splunk01:8089'
SPLUNK_USER='admin'
SPLUNK_PASSWORD='changeme'

SPLUNK_LOGIN    = SPLUNK_URL + '/services/auth/login?output_mode=json'
SPLUNK_JOB      = SPLUNK_URL + '/services/search/jobs?output_mode=json'
SPLUNK_STATUS   = SPLUNK_URL + '/services/search/jobs/%s/?output_mode=json'
SPLUNK_RESULT   = SPLUNK_URL + '/services/search/jobs/%s/results?output_mode=json&count=0'

searchquery = 'search index="_internal" | dedup host | fields host'
if not searchquery.startswith('search'):
    searchquery = 'search ' + searchquery

def splunk_login():
    # TODO: Support kerberos
    # TODO: Store creds under ~/.config/splunkinv.conf
    # TODO: How long does the session id work? Possible to reuse it and store it persistently?
    s = requests.Session()
    login = s.post(SPLUNK_LOGIN, verify=sslverify,
            data={'username': SPLUNK_USER, 'password': SPLUNK_PASSWORD})

    if login.status_code == 401:
        raise Exception('Login failed: %s' % login.json())
    elif not login.ok:
        raise Exception('Failure logging in: %s' % login.text)

    s.headers.update({'Authorization': 'Splunk %s' % login.json()['sessionKey']})
    return s

def splunk_search():
    s = splunk_login()

    searchjob = s.post(SPLUNK_JOB, data={'search': searchquery}, verify=sslverify)
    sid = searchjob.json()['sid']

    # Wait for 2 minutes and 1200 requests for search to finish.
    # Spam, bacon, sausage and Spam.
    done = False
    limit = 0
    while not done or limit > 1200:
        status = s.get(SPLUNK_STATUS % sid, verify=sslverify)
        done = all(x['content']['isDone'] == True for x in status.json()['entry'])
        limit = limit + 1
        if not done:
            sleep(0.1)

    result = s.get(SPLUNK_RESULT % sid, verify=sslverify)
    return result.json()['results']

def inventory(result):
    return {'all': {
                'hosts': [x['host'] for x in result],
                'vars': {}
            }}

def main():
    result = splunk_search()
    print(json.dumps(inventory(result), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
