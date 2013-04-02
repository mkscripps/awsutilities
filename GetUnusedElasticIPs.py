#\
# Created with PyCharm.
# User: mkelly
# Date: 3/12/13
# Time: 11:13 AM
# 
# Description:  Find unallocated Elastic IP Addresses and delete them.
#
#/
__author__ = 'mkelly'

import boto
#from boto import regioninfo
from boto import ec2
import string

ec2_region = ec2.get_region(
    region_name='us-east-1')

conn = boto.ec2.EC2Connection(
    region=ec2_region)

ElasticIPs=conn.get_all_addresses()
print "Total EIPS: %s" % len(ElasticIPs)
print "{0:20s} {1:20s} {2:11s} {3:18s} {4:18s}".format("Public IP", "Private IP", "Instance ID", "Association ID","Allocation ID")
for a in ElasticIPs:
    print "{0:20s} {1:20s} {2:11s} {3:18s} {4:18s}".format(a.public_ip, a.private_ip_address, a.instance_id, a.association_id,a.allocation_id)
    if a.instance_id is None or a.instance_id == "":
        print "No Associated InstanceID for %s, Deleting" % a.public_ip
        success = a.delete()
        if not success:
            print "Failed to delete ip %s" % (a.public_ip)
