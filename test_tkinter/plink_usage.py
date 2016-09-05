#!/usr/bin/python

import os
import sys
import time
import subprocess
import re
import platform

import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

def check_connection(ping_result):
	result = re.findall(r'\((\d+)\% loss\)', ping_result)
	lost_percent = result[0]
	if lost_percent == '0':
		return True
	return False

def test_ping(host_ip):
	"""
	Returns True if host responds to a ping request
	"""
	pPing = subprocess.Popen(['ping', '-n', '1', host_ip],
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	output, err = pPing.communicate()
	rc = pPing.returncode
	print output
	return check_connection(output)

r = test_ping('192.168.100.15')
if r == True:
	print("Connection established")
else:
	print("No Sirius device found")
	sys.exit(-1)

# Use trick
# https://deangrant.wordpress.com/2012/05/16/accept-server-host-key-when-automating-ssh-session-using-putty-plink/
# To avoid command promt when using putty/plink

os.system("echo y | " + current_dir + "\plink.exe -ssh -2 -pw 123 root@192.168.100.15 ls");

# pSsh = subprocess.Popen([current_dir + '\plink.exe', "-ssh", "-2", "-pw", "123", "root@192.168.100.15", "ls -al"],
# 	stdin=subprocess.PIPE,
# 	stdout=subprocess.PIPE,
# 	stderr=subprocess.PIPE)

# output, err = pSsh.communicate()
# rc = pSsh.returncode
# print output