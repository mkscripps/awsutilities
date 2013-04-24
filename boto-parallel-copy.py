#\
# Created with PyCharm.
# User: mkelly
# Date: 4/12/13
# Time: 12:27 PM
# 
# Description:  this script reads from the queue and performs multi-threaded, parallel copy commands.
# You run this script any number of times on any number of machines and it will pull the messages from the queue
# and perform the copy operations on many parallel threads.  You could load this script and call is as a UserData
# function in a EC2 instance launch of 10s of servers to optimize the parallelization.
#
#Options are:
# -a AWSRegion (optional.  Defaults to us-east-1)
# -q QueueName (required)
# -t MaxThreads to allow to run in parallel for a single file copy. (optional. Default is 1000)
# -b BlockSize - this controls the multi-part copy chunks sizes (optional. Default is 10485760.  10MB)
# -v Queue Message Visibility Timeout - this controls how long before the message is returned to the queue for another worker.  This is used in case the worker fails before the copy is complete and another worker needs to retry.  (optional. Default is 120)
# -s Queue retries before exiting - this is the concurrent number of queue message read retries with 10s between that will occur before the process assumes the queue is empty and exits (optional. Default is 20. 200 seconds.)
#
# Calling example:
# python boto-parallel-copy.py -q botoCopyQueue -r us-east-1 -t 1000 -b 10000000 -v 120 -s 20
#/
__author__ = 'mkelly'

import boto
import time
import threading
import boto.sqs
import json
import getopt
import sys
from boto.sqs.message import RawMessage
from collections import deque
from boto.s3.connection import OrdinaryCallingFormat


class uploadThread(threading.Thread):
    def __init__(self, b1, k1, k2, block, start, end):
        threading.Thread.__init__(self)
        self.name = block
        self.b1 = b1
        self.k1 = k1
        self.k2 = k2
        self.block = block
        self.startByte = start
        self.endByte = end

    def run(self):
        self.k2.copy_part_from_key(self.b1, self.k1, self.block, self.startByte, self.endByte)
        pool.release()


# collect inputs
optlist, args = getopt.getopt(sys.argv[1:], 'q:r:v:b:t:s:')

optdict = dict(optlist)

awsRegion = optdict['-r'] if '-r' in optlist else 'us-east-1'
messageQueueName = optdict['-q']
messageVisibilityTimeout = int(optdict['-v']) if '-v' in optdict else 60*2
maxthreads = int(optdict['-t']) if '-t' in optdict else 100
blocksize = int(optdict['-b']) if '-b' in optdict else 1024*1024*10
maxMissesBeforeShutdown = int(optdict['-s']) if '-s' in optdict else 20

pool = threading.BoundedSemaphore(value=maxthreads)
# make sure the queue is available
sqs = boto.sqs.connect_to_region(awsRegion)
messageQueue = sqs.get_queue(messageQueueName)
messageQueue.set_message_class(RawMessage)

if messageQueue is None:
    print "Queue: " + messageQueueName + " does not exist in Region: " + awsRegion
    print "Exiting..."
    exit()

concurrentMessageMisses = 0
while 1:
    if concurrentMessageMisses == maxMissesBeforeShutdown:
        print "Queues seems empty. Shutting down..."
        exit()

    messages = messageQueue.get_messages(visibility_timeout=messageVisibilityTimeout)
    if len(messages) == 0:
        concurrentMessageMisses += 1
        time.sleep(10)
        continue
    else:
        concurrentMessageMisses = 0

    message = messages[0]
    mBody = message.get_body()
    payload = json.loads(mBody)

    print payload

    start = time.time()

    k2mpu = None
    k1size = 0

    s3 = boto.connect_s3()
    b1 = s3.get_bucket(payload['sourceBucket'])
    b2 = s3.get_bucket(payload['targetBucket'])
    if b1 is None:
        print "Source bucket: " + payload['sourceBucket'] + " does not exist."
        messageQueue.delete_message(message)
        continue
    if b2 is None:
        print "Target bucket: " + payload['targetBucket'] + " does not exist."
        messageQueue.delete_message(message)
        continue

    k1 = b1.get_key(payload['sourceKey'])
    k2 = b2.get_key(payload['targetKey'])

    if k1 is None:
        print "Key does not exist: " + payload['sourceKey'] + " Bucket: " + payload['sourceBucket']
        messageQueue.delete_message(message)
        continue
    else:
        k1size = int(k1.size)

    if k1.size == 0:
        k1.copy(payload['targetBucket'], payload['targetKey'])
        messageQueue.delete_message(message)
        continue

    if k2 is None:
        k2mpu = b2.initiate_multipart_upload(payload['targetKey'])
    elif k2 is not None:
        k1size = int(k1.size)
        k2size = int(k2.size)
        if k1size != k2size:
            k2mpu = b2.initiate_multipart_upload(payload['targetKey'])

    if k2mpu is None:
        print "File: " + payload['targetKey'] + " in Bucket: " + payload['sourceBucket'] + " not copied since it exists and is the same size as the source."
        messageQueue.delete_message(message)
    else:
        lastThread = 0
        loops = int(k1size) /int(blocksize) + 1
        print "loops: %i" % loops

        threads = deque()

        print "Starting block copy of " + str(loops+1) + " blocks."

        if loops <= maxthreads:
            for i in range(loops):
                if (i+1)*blocksize < k1size:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, i+1, i*blocksize, (i+1)*blocksize-1)
                else:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, i+1, i*blocksize, k1size-1)
                pool.acquire()
                new_thread.start()
                threads.append(new_thread)
        else:
            for i in range(maxthreads):
                if (i+1)*blocksize < k1size:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, i+1, i*blocksize, (i+1)*blocksize-1)
                else:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, i+1, i*blocksize, k1size-1)
                pool.acquire()
                new_thread.start()
                threads.append(new_thread)
                lastThread = i

        print "Waiting for " + str(len(threads)) + " threads to complete..."
        if lastThread != 0 and lastThread <= loops:
            print "Adding more threads..."
        while len(threads) > 0:
            t = threads.pop()
            if len(threads) == 0:
                t.join()
            if lastThread != 0 and lastThread <= loops:
                sys.stdout.write('.')
                if (lastThread+1)*blocksize < k1size:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, lastThread+1, lastThread*blocksize, (lastThread+1)*blocksize-1)
                elif k1size == 0:
                    new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, lastThread+1, lastThread*blocksize, 0)
                else:
                    if lastThread*blocksize < (k1size-1):
                        new_thread = uploadThread(payload['sourceBucket'], payload['sourceKey'], k2mpu, lastThread+1, lastThread*blocksize, k1size-1)
                    break
                pool.acquire()
                new_thread.start()
                threads.append(new_thread)
                lastThread += 1
        print "Threads completed."
        k2mpu.complete_upload()
        messageQueue.delete_message(message)
        print "Total upload time for Key: " + payload['targetKey'] + " in "+ str(time.time() - start) + " seconds."




