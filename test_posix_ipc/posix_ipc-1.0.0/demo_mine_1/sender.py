# 3rd party modules
import posix_ipc
from demo_global import *

print "Sender program"

# Create the message queue.
try:
	mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME, posix_ipc.O_CREX)
except:
	print "Messque queue already created, open it"
	mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME)

mq.send("Hello world")
print "Hello world sent"

