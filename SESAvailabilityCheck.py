#\
# Created with PyCharm.
# User: mkelly
# Date: 4/3/13
# Time: 4:54 PM
# 
# Description:
#
#/
__author__ = 'mkelly'

import smtplib

def prompt(prompt):
    return raw_input(prompt).strip()

fromaddr = "mark.kelly@scrippsnetworks.com"
toaddrs  = "mekelly5@gmail.com"
print "Enter message, end with ^D (Unix) or ^Z (Windows):"

# Add the From: and To: headers at the start!
msg = ("From: %s\r\nTo: %s\r\n\r\n"
       % (fromaddr, toaddrs))
msg = msg + '\r\nSubject: Test Message\r\nTesting SES availability\r\n\r\n'

print "Message length is " + repr(len(msg))

server = smtplib.SMTP('email-smtp.us-east-1.amazonaws.com',25)
server.starttls()
server.login('AKIAJH6WTFH5A4ZBVIBA','AqHYHrtsxLTQFDiQVi/XUSATvAfAkbz3sCL6PHN/vlf6')

server.set_debuglevel(1)
server.sendmail(fromaddr, toaddrs, msg)
server.quit()