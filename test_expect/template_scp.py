import pexpect
from pexpect import pxssh
import sys
import os

if len(sys.argv) != 6:
	print "Syntax: "
	print "\t%s <hostname> <username> <password> <file-to-copy> <remote-path-to-copy-to>" % (os.path.basename(__file__))
	sys.exit(1)

hostname = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]
file = sys.argv[4]
dest = sys.argv[5]

# Just workaroud way to enable to login target host
s = pxssh.pxssh()
s.login(hostname, username, password)
print "Login ok"
s.logout()

# Not copy a file to target
print 'scp %s %s@%s:%s' % (file, username, hostname, dest)
child = pexpect.spawn('scp %s %s@%s:%s' % (file, username, hostname, dest))
child.expect('%s@%s\'s password: ' % (username, hostname))
child.sendline(password)
child.expect(pexpect.EOF)
print "Scp ok"
