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
bucket = conn.get_bucket('sni-transcode')
for key in bucket.list():
    #due to 5gb limit need to check object size and make sure it is already "STANDARD" storage class
    if key.size < 5*1024*1024*1024 and key.storage_class == 'STANDARD':
        key.change_storage_class('REDUCED_REDUNDANCY')
    print "%40s %19s %s" % (key.name.encode('utf-8'),key.storage_class,key.size)
