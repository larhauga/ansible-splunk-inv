#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
sslverify = True

from xml.dom import minidom

SPLUNK_URL='https://searchhead:8089'
SPLUNK_USER='admin'
SPLUNK_PASSWORD='changeme'

searchquery = 'search index="_internal" | dedup host | fields host'
if not searchquery.startswith('search'):
    searchquery = 'search ' + searchquery

def splunk_search():
    r = requests.post(SPLUNK_URL + '/services/auth/login?output_mode=json',
            data={'username': SPLUNK_USER, 'password': SPLUNK_PASSWORD},
            verify=sslverify)
    sessionkey = r.json()['sessionKey']

    searchjob = requests.post(SPLUNK_URL + '/services/search/jobs?output_mode=json',
            headers={'Authorization': 'Splunk %s' % sessionkey},
            data={'search': searchquery}, verify=sslverify)
    sid = searchjob.json()['sid']

    done = False
    while not done:
        status = requests.get(SPLUNK_URL + '/services/search/jobs/%s/?output_mode=json' % sid,
                headers={'Authorization': 'Splunk %s' % sessionkey}, verify=sslverify)
        done = all(x['content']['isDone'] == True for x in status.json()['entry'])

    result = requests.get(SPLUNK_URL + '/services/search/jobs/%s/results?output_mode=json&count=0' % sid,
            headers={'Authorization': 'Splunk %s' % sessionkey}, verify=sslverify)
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
