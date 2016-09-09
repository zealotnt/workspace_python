# 3rd party modules
import posix_ipc
from demo_global import *
import time
import sys
import threading

threads = []
time_start = float(time.time() * 1000)
time_check = float(time.time() * 1000)

thread_killed = False
def KeepProtectedSessionAlive():
	mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME)
	while thread_killed == False:
		mq.send('\x05\x00\xff\xff\xaa\xcc\x00')
		time.sleep(1)

# Wait for at most 2s to message queue to created
success = 0
while (time_check - time_start) < 2000:
	try:
		time_check = float(time.time() * 1000)	
		mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME)
		t = threading.Thread(target=KeepProtectedSessionAlive)
		t.start()
		success = 1
	except:
		continue
	break

if success != 1:
	print "No message queue"
	exit(-1)

time.sleep(3)

thread_killed = True