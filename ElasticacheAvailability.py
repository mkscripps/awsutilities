#\
# Created with PyCharm.
# User: mkelly
# Date: 4/3/13
# Time: 1:42 PM
# 
# Description:
#
#/
__author__ = 'mkelly'
import getpass
import sys
import telnetlib

HOST = "aim-dev1-c.f6ovjk.cfg.use1.cache.amazonaws.com"
PORT = "11211"

tn = telnetlib.Telnet(HOST,PORT)
print tn.read_all()
#write record into cache
tn.read_until("Escape character")
tn.write("a 0 0 5\n")
tn.write("hello\n")
tn.read_until("STORED")

#Read cached record
tn.write("get a\n")
tn.read_until("hello")
print tn.read_all()
print "success"