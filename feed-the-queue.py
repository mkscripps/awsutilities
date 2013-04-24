#\
# Created with PyCharm.
# User: mkelly
# Date: 4/12/13
# Time: 12:23 PM
# 
# Description:  This script reads from a bucket and creates an SQS message for each file that needs to be copied.
# You run this first to load up the work.  All files will be added to the queue.
# Skipping duplicates and unnecessary copies is handled in the other script.
#
# Options are:
# -a AWSRegion (optional.  Defaults to us-east-1)
# -q QueueName (required)
# -s SourceBucket (required)
# -f Filter - this is a filter to use in the list bucket. This would be useful to get everything below a certain
#               folder. (optional)
# -t TargetBucket (required)
# -p Prefix - this will prepend a prefix to the name on the target bucket.  Useful for creating an alternate folder
#               root in the target. (optional)
#
# Calling example:
# python feed-the-queue.py -q botoCopyQueue -s maddog-public-share -t mtavis-public-share -f media -p /copyFolder2/
#
#/
__author__ = 'mkelly'

import boto
import boto.sqs
import json
import uuid
import sys
import getopt
from boto.sqs.message import Message
from boto.sqs.message import RawMessage
from boto.sqs.queue import Queue

optlist, args = getopt.getopt(sys.argv[1:], 'q:r:s:f:t:p:oc')

print optlist

optdict = dict(optlist)

awsRegion = optdict['-r'] if '-r' in optlist else 'us-east-1'

s3 = boto.connect_s3()
sqs = boto.sqs.connect_to_region(awsRegion)

# collect inputs
sourceBucket = optdict['-s']
sourceFilter = optdict['-f'] if '-f' in optdict else ''
targetBucket = optdict['-t']
targetPrefix = optdict['-p'] if '-p' in optdict else ''
messageQueueName = optdict['-q']
forceOverwrite = '-o' in optdict
createQueue = '-c' in optdict
messageBatchSize = 10

# s3 listing
b1 = s3.get_bucket(sourceBucket)
b1keys = b1.list(sourceFilter)

# make sure the queue is available
messageQueue = sqs.get_queue(messageQueueName)

if messageQueue is None and not createQueue:
    print "Queue: " + messageQueueName + " does not exist in Region: " + awsRegion
    print "Exiting..."
    exit()
elif messageQueue is None and createQueue:
    messageQueue = sqs.create_queue(messageQueueName)
    qName = messageQueue.name
    print "Created Queue: " + qName + " in Region: " + awsRegion + "."

# feed the queue
messagesWritten = 0
batch = []
for k in b1keys:
    sourceBucket = k.bucket.name
    sourceKey = k.name
    payload = {'sourceBucket': sourceBucket, 'sourceKey': sourceKey, 'targetBucket': targetBucket, 'targetKey': targetPrefix + sourceKey, 'overwrite': False}
    m = Message()
    m.set_body(json.dumps(payload))
    batch.append([uuid.uuid4(), json.dumps(payload), 0])
    if len(batch) == messageBatchSize:
        status = messageQueue.write_batch(batch)
        messagesWritten += 10
        batch = []

# sending remaining messages in a small batch
if len(batch) > 0:
    status = messageQueue.write_batch(batch)
    messagesWritten += len(batch)

# closeout
print str(messagesWritten) + " messages written to Queue: " + messageQueue.name + " in Region: " + awsRegion + "."
