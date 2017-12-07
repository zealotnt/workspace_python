from pexpect import pxssh
import pexpect, getpass
import sys
import os
from pyexpect_common import *
from template_ifconfig_ip import *
from template_scp import *

def CopyBaseline():
	SetNetworkInterface(HOST_INTERFACE, HOST_IP, HOST_PASSWORD)
	ScpDownloadFrom("/home/root/fw_backup/baseline", "root", BOARD_PASSWORD, BOARD_IP, "./")

if __name__ == '__main__':
	CopyBaseline()
