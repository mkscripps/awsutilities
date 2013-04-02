#\
# Created with PyCharm.
# User: mkelly
# Date: 2/4/13
# Time: 3:52 PM
# 
# Description:
#
#/
__author__ = 'mkelly'


import socket
import argparse

parser = argparse.ArgumentParser(description='Check if host exists, returns one if hostname resolves, 0 otherwise')
parser.add_argument('hostname', metavar='hostname', type=str, nargs=1,
    help='hostname of ip to check for existence')

args = parser.parse_args()

def hostname_resolves(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1
    except socket.error:
        return 0

print hostname_resolves(args.hostname[0])

