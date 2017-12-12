import pexpect
import sys
import os
from pyexpect_common import *
from dotenv import load_dotenv

# Common config
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path, verbose=True)
HOST_USERNAME = os.environ.get('HOST_USERNAME')
HOST_PASSWORD = os.environ.get('HOST_PASSWORD')
HOST_IP = os.environ.get('HOST_IP')
HOST_INTERFACE = os.environ.get('HOST_INTERFACE')
TARGET_PASSWORD = os.environ.get('TARGET_PASSWORD')
TARGET_IP = os.environ.get('TARGET_IP')
TARGET_USERNAME = os.environ.get('TARGET_USERNAME')

# Constant
PYEXPECT_INFO_HDR = "[PY_EXPECT_INFO] "
PYEXPECT_CMD_HDR = "[PY_EXPECT_CMD] "

def PyexpectInfo(msg):
	print PYEXPECT_INFO_HDR + msg

def PrintCommand(pyexpect_spawn_obj):
	cmd_str = ""
	for cmd in pyexpect_spawn_obj.args:
		cmd_str += cmd + " "
	print (PYEXPECT_CMD_HDR + cmd_str)
	return cmd_str
