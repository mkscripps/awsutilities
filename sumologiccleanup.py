#\
# Created with PyCharm.
# User: mkelly
# Date: 4/1/13
# Time: 3:56 PM
# 
# Description: Cleanup disconnected agents in Sumo Logic
#
#/
__author__ = 'mkelly'

import requests
from requests.auth import HTTPBasicAuth
import json

#import username and password from local config.py file
# this file only contains:
#       username = xxxxxxx
#       password = xxxxxxx
#
from config import *

DEBUG = True

#Get a list of collectors from Sumo
#
r = requests.get('https://api.sumologic.com/api/v1/collectors', auth=HTTPBasicAuth(username, password))

collectors = r.json()

collectorsToDelete = []

for collector in collectors['collectors']:
    #check to see if it is alive
    #
    if collector['alive'] is False:
        collectorsToDelete.append(collector)
        print collector['id']

print "There are %i Collectors that are not reporting and could be deleted" % (len(collectorsToDelete))

#Delete dead collectors
for collector in collectorsToDelete:
    try:
        if DEBUG is False:
            r = requests.delete('https://api.sumologic.com/api/v1/collectors/%s' % (collector['id']),
                                auth=HTTPBasicAuth(username, password))
            if r.status_code != 200:
                print "delete failed for the following collector %s" % (collector['id'])
                print "status code: %s" % r.status_code
                print "reason: %s" % r.reason
            else:
                print "deleted collector %s" % collector['id']

        else:
            print 'https://api.sumologic.com/api/v1/collectors/%s' % (collector['id'])
            print "deleted collector %s" % collector['id']
    except:
        print "could not delete %s " % collector['id']
