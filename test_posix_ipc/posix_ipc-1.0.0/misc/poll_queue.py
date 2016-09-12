# 3rd party modules
import posix_ipc
from demo_global import *
import time
import sys
import threading

class ProtectedSessionThread(threading.Thread):
	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.shouldKilled = False
		self._queue_name = ""

	def run(self):
		print "Starting " + self.name
		self.KeepProtectedSessionAlive(self._queue_name)
		print "Exiting " + self.name

	# Wait for at most 2s to message queue to created
	def WaitForMsgQueue(self, queue_name):
		self._queue_name = queue_name
		time_start = float(time.time() * 1000)
		time_check = float(time.time() * 1000)
		while (time_check - time_start) < 2000:
			try:
				time_check = float(time.time() * 1000)
				mq = posix_ipc.MessageQueue(queue_name)
				print "Found msg queue " + queue_name
				return True
			except:
				continue
		print "Msq queue " + queue_name + " not found"
		return False

	def KeepProtectedSessionAlive(self, queue_name):
		mq = posix_ipc.MessageQueue(queue_name)
		while self.shouldKilled == False:
			mq.send('\x05\x00\xff\xff\xaa\xcc\x00')
			time.sleep(1)
			print "ProtectedSession keep alive"

	def StopThread(self):
		self.shouldKilled = True

protected_session = ProtectedSessionThread("Protected Session")

if protected_session.WaitForMsgQueue(MSQ_QUEUE_OBJ_NAME) == False:
	sys.exit(-1)
protected_session.start()

try:
	while True:
		time.sleep(1)
finally:
	protected_session.StopThread()
