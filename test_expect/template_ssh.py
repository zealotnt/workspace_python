from pexpect import pxssh
import sys
import os
from pyexpect_common import *
from template_scp import *

def SshLoginInteractive(remote_ipaddress, remote_username, remote_password):
	# Download "target" to our machine
	retry = True
	while retry:
		child = pexpect.spawn('ssh %s -l %s ' % (remote_ipaddress, remote_username))
		PrintCommand(child)
		expect_remote_password = '%s@%s\'s password: ' % (remote_username, remote_ipaddress)
		i = child.expect(['Host key verification failed.', expect_remote_password, 'yes/no'])
		if i == 0: # need to clear SSH Key
			SshRemoveKey(host_user_name, remote_ipaddress)
		elif i == 1: # send remote_password
			child.sendline(remote_password)
			retry = False
		elif i == 2: # need to prompt yes (to add SSH key to known_host)
			child.sendline("yes")
		else: # something wrong
			print ("Sth wrong")
			pass
	child.interact()

def SshLoginModule(hostname, username, password):
	s = pxssh.pxssh()
	s.login(hostname, username, password)
	print "Login ok"
	s.interact()
	s.logout()

def main():
	if len(sys.argv) != 4:
		print "Syntax: "
		print "\t%s <hostname> <username> <password>" % (os.path.basename(__file__))
		sys.exit(1)

	hostname = sys.argv[1]
	username = sys.argv[2]
	password = sys.argv[3]

	# SshLoginModule(hostname, username, password)
	SshLoginInteractive(hostname, username, password)

if __name__ == '__main__':
	main()
