#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import json
import argparse
import requests
import ConfigParser
from time import sleep
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
sslverify = False

config = ConfigParser.ConfigParser()
config.read(['splunkinv.conf',
    os.path.expanduser('~/.config/splunkinv.conf'),
    os.path.join(os.getcwd(), os.path.dirname(__file__), 'splunkinv.conf')])

try:
    SPLUNK_KRB = config.getboolean('splunkinv','kerberos')
    SPLUNK_URL=config.get('splunkinv','url')

    if not SPLUNK_KRB:
        SPLUNK_USER=config.get('splunkinv','user')
        SPLUNK_PASSWORD=config.get('splunkinv','password')
    else:
        from requests_kerberos import HTTPKerberosAuth, REQUIRED

except (ConfigParser.NoOptionError, ConfigParser.NoSectionError):
    raise Exception('No login method available.')

SPLUNK_LOGIN    = SPLUNK_URL + '/services/auth/login?output_mode=json'
SPLUNK_JOB      = SPLUNK_URL + '/services/search/jobs?output_mode=json'
SPLUNK_STATUS   = SPLUNK_URL + '/services/search/jobs/%s/?output_mode=json'
SPLUNK_RESULT   = SPLUNK_URL + '/services/search/jobs/%s/results?output_mode=json&count=0'

def splunk_login():
    # TODO: Support kerberos
    # https://github.com/requests/requests-kerberos
    # TODO: Store creds under ~/.config/splunkinv.conf
    # TODO: How long does the session id work? Possible to reuse it and store it persistently?
    s = requests.Session()
    if SPLUNK_KRB:
        kerberos_auth = HTTPKerberosAuth(mutual_authentication=REQUIRED, sanitize_mutual_error_response=False)
        login = s.post(SPLUNK_LOGIN, verify=sslverify, auth=kerberos_auth)
    else:
        login = s.post(SPLUNK_LOGIN, verify=sslverify,
                data={'username': SPLUNK_USER, 'password': SPLUNK_PASSWORD})

    if login.status_code == 401:
        raise Exception('Login failed: %s' % login.json())
    elif not login.ok:
        raise Exception('Failure logging in: %s' % login.text)

    s.headers.update({'Authorization': 'Splunk %s' % login.json()['sessionKey']})
    return s

def splunk_search(searchquery):
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
    # TODO: Support _meta hostvars with searchresult
    # TODO: Handle no returned hosts
    return {'all': {'hosts': [x['host'] for x in result]}}

def main():
    search = None
    parser = argparse.ArgumentParser(description='Ansible inventory for splunk')
    parser.add_argument('search', type=str, nargs='?', help='Splunk search. Use quotes or escape them')
    args = parser.parse_args()

    try:
        if os.environ['SQ']:
            # print("Using ENVIRON SQ")
            search = os.environ['SQ']
        elif args.search:
            # print("Using argument")
            if type(args.search) == list:
                search = " ".join(args.search)
            else:
                search = args.search
        elif os.path.isfile('splunk.search'):
            search = " ".join([line.rstrip('\n') for line in open('splunk.search')])
    except KeyError as e:
        pass

    if not search:
        raise Exception("Splunk search not found. ENV['SQ'], arg string (-h) og file 'splunk.search'")
    else:
        # searchquery = 'search index="_internal" | dedup host | fields host'
        if not search.startswith('search'):
            searchquery = 'search ' + search

    result = splunk_search(searchquery)
    print(json.dumps(inventory(result), sort_keys=True, indent=2))

if __name__ == '__main__':
    main()
