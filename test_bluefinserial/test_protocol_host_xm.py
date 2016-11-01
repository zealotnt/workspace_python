#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# datalink_deliver.py


# ---- IMPORTS
import os
import re
import time
import sys
import serial
import struct
from optparse import OptionParser, OptionGroup

sys.path.insert(0, 'bluefinserial')
from datalink_deliver import BluefinserialSend, BluefinserialCommand
from scan import scan
from utils import *

# ---- CONSTANTS
USAGE = u"""Usage:
test_protocol <len-to-send> <len-expected-to-receive>
"""

def increase_str_by_one(value):
	int_val = ord(value)
	int_val += 1
	int_val &= 0xFF
	return chr(int_val)

if len(sys.argv) != 3:
	print USAGE
	sys.exit(-1)

send_buff = ''
cmd_len = int(sys.argv[1])
rsp_len = int(sys.argv[2])

if cmd_len < 10:
	print_err("Command len should be bigger than 10")
	sys.exit(-1)
if cmd_len > 510:
	print_err("Command len should be less than or equal to 510")
	sys.exit(-1)
if rsp_len < 6:
	print_err("Expected response len should be bigger than 6 (2 bytes Cmd + Ctr, 4 bytes len)")
	sys.exit(-1)
if rsp_len > 510:
	print_err("Expected response len should be less than or equal to 510")
	sys.exit(-1)

send_buff = struct.pack('<II', cmd_len, rsp_len)

idx = 0
pos_val = '\x00'
while idx < cmd_len:
	pos_val = increase_str_by_one(pos_val)
	send_buff += pos_val
	idx += 1

comm = BluefinserialSend("/dev/ttyACM0", 115200)

pkt = BluefinserialCommand(BluefinserialCommand.TARGET_APPLICATION)
cmd = pkt.Packet('\x10', '\x7e', send_buff)
rsp = ''


times = 1
while True:
	# dump_hex(cmd, "Command: ")
	start = int(round(time.time() * 1000))
	rsp = comm.Exchange(cmd)
	if rsp is None:
		print_err("Transmit fail")
		sys.exit(-1)

	# dump_hex(rsp, "Response: ")
	end = int(round(time.time() * 1000))
	print "Send %d times, %.2gms" % (times, ((end-start)*1000))
	times += 1

