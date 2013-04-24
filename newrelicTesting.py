#\
# Created with PyCharm.
# User: mkelly
# Date: 4/19/13
# Time: 3:10 PM
# 
# Description:
#
#/
__author__ = 'mkelly'

import requests

headers = {'x-api-key': '24429695e098e3e2ed8fd1ac503c6318c09ee3da9af7754'}
accountID = "209454"

#https://api.newrelic.com/api/v1/accounts.xml

r = requests.get('https://api.newrelic.com/api/v1/accounts/209454/server_settings.xml', headers=headers)
#r = requests.get('https://api.newrelic.com/api/v1/accounts.xml', headers=headers)

print r.text

#get all server settings
#r = requests.get('api.newrelic.com/api/v1/accounts/209454/server_settings.xml', headers=headers)
#api.newrelic.com/api/v1/accounts/:account_id/server_settings.xml
