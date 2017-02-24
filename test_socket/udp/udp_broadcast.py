#!/usr/bin/python
# Send UDP broadcast packets

MYPORT = 9

import sys, time
from socket import *

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('', 0))
s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

while 1:
	data = "Hello from %s" % sys.argv[1]
	print "Sending %s" % data
	s.sendto(data, ('<broadcast>', MYPORT))
	time.sleep(2)
