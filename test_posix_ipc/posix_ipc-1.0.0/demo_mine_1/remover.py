# 3rd party modules
import posix_ipc
from demo_global import *
 
print "Remover programm, remove the message queue"

# Create the message queue.
mq = posix_ipc.MessageQueue(MSQ_QUEUE_OBJ_NAME)
mq.unlink()
