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

SPLUNK_LOGIN=SPLUNK_URL + '/services/auth/login?output_mode=json'
SPLUNK_JOB=SPLUNK_URL + '/services/search/jobs?output_mode=json'
SPLUNK_STATUS=SPLUNK_URL + '/services/search/jobs/%s/?output_mode=json'
SPLUNK_RESULT=SPLUNK_URL + '/services/search/jobs/%s/results?output_mode=json&count=0'

searchquery = 'search index="_internal" | dedup host | fields host'
if not searchquery.startswith('search'):
    searchquery = 'search ' + searchquery

def splunk_search():
    login = requests.post(SPLUNK_LOGIN, verify=sslverify,
            data={'username': SPLUNK_USER, 'password': SPLUNK_PASSWORD})
    auth = {'Authorization': 'Splunk %s' % login.json()['sessionKey']}

    searchjob = requests.post(SPLUNK_JOB, headers=auth,
            data={'search': searchquery}, verify=sslverify)
    sid = searchjob.json()['sid']

    done = False
    while not done:
        status = requests.get(SPLUNK_STATUS % sid, headers=auth, verify=sslverify)
        done = all(x['content']['isDone'] == True for x in status.json()['entry'])
        sleep(0.1)

    result = requests.get(SPLUNK_RESULT % sid, headers=auth, verify=sslverify)
    return result.json()['results']

def inventory(result):
    return {
            'all': {
                'hosts': [x['host'] for x in result],
                'vars': {}
            }}

def main():
    result = splunk_search()
    print(json.dumps(inventory(result), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
