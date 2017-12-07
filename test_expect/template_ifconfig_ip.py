import pexpect
import sys
import os
from pyexpect_common import *

def SetNetworkInterface(interface, ipaddress, password):
	child = pexpect.spawn('sudo ifconfig %s %s' % (interface, ipaddress))
	child.logfile = sys.stdout
	PrintCommand(child)
	child.expect('[sudo] .*: ')
	child.sendline(password)
	child.expect(pexpect.EOF)
	PyexpectInfo("Done set [interface] %s to [ip] %s" % (interface, ipaddress))

if __name__ == '__main__':
	if len(sys.argv) != 4:
		print "Syntax: "
		print "\t%s <interface> <ipaddress> <password>" % (os.path.basename(__file__))
		sys.exit(1)

	interface = sys.argv[1]
	ipaddress = sys.argv[2]
	password = sys.argv[3]
	SetNetworkInterface(interface, ipaddress, password)
