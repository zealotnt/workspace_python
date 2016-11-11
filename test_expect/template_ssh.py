from pexpect import pxssh
import sys
import os

if len(sys.argv) != 4:
	print "Syntax: "
	print "\t%s <hostname> <username> <password>" % (os.path.basename(__file__))
	sys.exit(1)

hostname = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

s = pxssh.pxssh()
s.login(hostname, username, password)
print "Login ok"
s.interact()
s.logout()
