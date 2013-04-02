#\
# Created with PyCharm.
# User: mkelly
# Date: 3/6/13
# Time: 2:21 PM
# 
# Description:
#
#/
__author__ = 'mkelly'
import boto
from boto import regioninfo
from boto import ec2

elb_region = boto.regioninfo.RegionInfo(
    name='us-east-1',
    endpoint='elasticloadbalancing.us-east-1.amazonaws.com')

elb_connection = boto.connect_elb(
    region=elb_region)

ec2_region = ec2.get_region(
    region_name='us-east-1')

ec2_connection = boto.ec2.connection.EC2Connection(
    region=ec2_region)

load_balancer = elb_connection.get_all_load_balancers(load_balancer_names=['awseb-e-z-AWSEBLoa-JWYM2Z2T15B3'])[0]
instance_ids = [ instance.id for instance in load_balancer.instances ]

reservations = ec2_connection.get_all_instances(instance_ids)
instance_addresses = [ i.public_dns_name for r in reservations for i in r.instances ]

print instance_ids
print instance_addresses