import pexpect
import sys
import os
from pyexpect_common import *

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
