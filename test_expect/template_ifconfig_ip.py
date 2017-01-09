import pexpect
import sys
import os

if len(sys.argv) != 4:
	print "Syntax: "
	print "\t%s <interface> <ipaddress> <password>" % (os.path.basename(__file__))
	sys.exit(1)

interface = sys.argv[1]
ipaddress = sys.argv[2]
password = sys.argv[3]

child = pexpect.spawn('sudo ifconfig %s %s' % (interface, ipaddress))
child.expect('[sudo] .*: ')
child.sendline(password)
