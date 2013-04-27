#\
# Created with PyCharm.
# User: mkelly
# Date: 4/27/13
# Time: 10:55 AM
# 
# Description:  set all keys in a bucket to reduced redundancy
#
#/
__author__ = 'mkelly'


from boto.s3.connection import S3Connection

conn = S3Connection()
bucket = conn.get_bucket('sn-amazon')
for key in bucket.list():
    #due to 5gb limit need to check object size
    if key.size < 5*1024*1024*1024:
        key.change_storage_class('REDUCED_REDUNDANCY')
        print "%s has been changed to Reduced redundancy storage" % key.name.encode('utf-8')
