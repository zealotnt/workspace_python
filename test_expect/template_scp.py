import pexpect
from pexpect import pxssh
import sys
import os
from pyexpect_common import *
from template_ifconfig_ip import *

# Just workaroud way to enable to login target host
def SshLogin():
	s = pxssh.pxssh()
	s.login(hostname, remote_username, password)
	print "Login ok"
	s.logout()

def SshRemoveKey(host_remote_username, remote_ipaddress):
	# Upload a "target" from our machine to host
	child = pexpect.spawn('ssh-keygen -f "/home/%s/.ssh/known_hosts" -R %s' % (host_remote_username, remote_ipaddress))
	child.logfile = sys.stdout
	PrintCommand(child)
	child.expect('known_hosts.old')
	PyexpectInfo("Done set remove ssh key of [ip] %s" % (remote_ipaddress))

def ScpUploadTo(target, remote_username, remote_password, remote_ipaddress, dest, host_user_name="zealot"):
	# Upload a "target" from our machine to host
	retry = True
	while retry:
		child = pexpect.spawn('scp -rp %s %s@%s:%s' % (target, remote_username, remote_ipaddress, dest))
		child.logfile = sys.stdout
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
	child.expect(pexpect.EOF)
	PyexpectInfo("Scp upload ok")

def ScpDownloadFrom(target, remote_username, remote_password, remote_ipaddress, dest, host_user_name="zealot"):
	# Download "target" to our machine
	retry = True
	while retry:
		child = pexpect.spawn('scp -rp %s@%s:%s %s' % (remote_username, remote_ipaddress, target, dest))
		child.logfile = sys.stdout
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
	child.expect(pexpect.EOF)
	PyexpectInfo("Scp download ok")

if __name__ == '__main__':
	# Example:
	# python template_scp.py usb0 "host_password_here" 192.168.100.16 192.168.100.15 root "" template_scp.py /home/root
	if len(sys.argv) != 9:
		print "Syntax: "
		prompt = "\t%s <interface> <host_password> <host_ipaddress>" % (os.path.basename(__file__))
		prompt += "<remote_ipaddress> <remote_username> <remote_password> <file-to-copy> <remote-path-to-copy-to>"
		print prompt
		sys.exit(1)

	interface = sys.argv[1]
	host_password = sys.argv[2]
	host_ipaddress = sys.argv[3]
	remote_ipaddress = sys.argv[4]
	remote_username = sys.argv[5]
	remote_password = sys.argv[6]
	file = sys.argv[7]
	dest = sys.argv[8]

	SetNetworkInterface(interface, host_ipaddress, host_password)
	ScpUploadTo(file, remote_username, remote_password, remote_ipaddress, dest)
	ScpDownloadFrom(dest+"/"+file, remote_username, remote_password, remote_ipaddress, "./")
