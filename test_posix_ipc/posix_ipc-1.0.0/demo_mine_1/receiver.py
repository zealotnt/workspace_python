# 3rd party modules
import posix_ipc
from demo_global import *

print "Receiver program"

# Create the message queue.
mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME)

s, _ = mq.receive()
s = s.decode()
print "Received %s" % s