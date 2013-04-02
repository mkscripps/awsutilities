#\
# Created with PyCharm.
# User: mkelly
# Date: 1/16/13
# Time: 3:17 PM
# To change this template use File | Settings | File Templates.
#/

import argparse

#TODO: Add stuff here

parser = argparse.ArgumentParser(description='Set and instance to unhealthy ')
parser.add_argument('instance', metavar='Instance', type=str, nargs=1,
                    help='Instance Id to set Health on ')
parser.add_argument('--status', metavar='Status', type=str, default='Healthy',
                    help='The health status of the instance. \"Healthy\" means that the instance is healthy and should remain in service. \"Unhealthy\" means that the instance is unhealthy. Auto Scaling should terminate and replace it.')
parser.add_argument('--grace', metavar='Respect_Grace_Period', type=bool, default=True,
                    help='If True, this call should respect the grace period associated with the group.')

args = parser.parse_args()

from boto.ec2.autoscale import AutoScaleConnection
conn = AutoScaleConnection()
conn.get_all_groups()
print args.status
conn.set_instance_health(args.instance[0],args.status,str(args.grace))

print args.instance[0], " has been marked", args.status[0]