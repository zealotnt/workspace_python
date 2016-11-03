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
from datalink_deliver import *
from scan import scan
from utils import *

# ---- CONSTANTS
USAGE = u"""Usage:
test_protocol <len-to-send> <len-expected-to-receive>
"""

PROTOCOL_TEST_HDR = "[Protocol test] "

def increase_str_by_one(value):
	int_val = ord(value)
	int_val += 1
	int_val &= 0xFF
	return chr(int_val)

def validate_response(count, exp_resp_len, resp):
	if len(resp) != (exp_resp_len):
		print_err("Invalid response len: " + str(len(resp)) + " should be " + str(exp_resp_len))
		return False
	if ord(resp[2]) + (ord(resp[3]) << 8) + (ord(resp[4]) << 16) + (ord(resp[5]) << 24) != count:
		print_err("Count value mismatch")
		return False

	idx = 0
	pos_val = '\x06'
	while idx < (exp_resp_len - 6): # exp_resp_len = 6 byte [header + tail] + payload
		if resp[idx + 6] != pos_val:
			print_err("Response buffer mismatch: " + format(ord(resp[idx + 5]), '02x') + " should be " + format(ord(pos_val), '02x'))
			return False
		pos_val = increase_str_by_one(pos_val)
		idx += 1
	return True

def prepare_buffer(cmd_len, rsp_len, count):
	# Prepare the sending buffer
	send_buff = struct.pack('<II', count, rsp_len)

	idx = 0
	pos_val = '\x00'
	while idx < cmd_len:
		pos_val = increase_str_by_one(pos_val)
		send_buff += pos_val
		idx += 1
	return send_buff

if __name__ == "__main__":
	parser = OptionParser()
	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						default=BLUEFINSERIAL_DEFAULT_SERIAL_PORT,
						help="define the serial port to use")
	parser.add_option(  "-b", "--baud",
						dest="baud",
						type="string",
						default=BLUEFINSERIAL_BAUDRATE,
						help="define the serial baudrate to use")
	parser.add_option(  "-p", "--package",
						dest="packages_size",
						default="",
						help="define the package to transmit/receive")
	parser.add_option(  "-t", "--target",
						dest="protocol_test_target",
						default="RF",
						help="define the target to test protocol, any of: RF/APP")

	(options, args) = parser.parse_args()

	if options.protocol_test_target == "RF":
		target = BluefinserialCommand.TARGET_RF
		cmd_code = '\x8b'
		ctr_code = '\x70'
	elif options.protocol_test_target == "APP":
		target = BluefinserialCommand.TARGET_APPLICATION
		cmd_code = '\x10'
		ctr_code = '\x7E'
	else:
		print_err("Invalid target to send")
		print_err("Only support target RF/APP with flag -t")
		sys.exit(-1)

	params = options.packages_size.split(',')
	if len(params) != 2:
		print_err("Please specify the Command len + Expected response len with format:")
		print_err("\t python test_protocol.py -p <Command_len>,<Expected_len>")
		sys.exit(-1)

	cmd_len = int(params[0])
	rsp_len = int(params[1])

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

	# Init the com port
	comm = BluefinserialSend(options.serial, options.baud)
	pkt = BluefinserialCommand(target)

	# Start testing
	times = 1
	while True:
		# Update sending package
		send_buff = prepare_buffer(cmd_len, rsp_len, times)
		cmd = pkt.Packet(cmd_code, ctr_code, send_buff)

		# dump_hex(cmd, "Command: ")
		start = int(round(time.time() * 1000))
		rsp = comm.Exchange(cmd)
		if rsp is None:
			print_err(PROTOCOL_TEST_HDR + "Transmit fail")
			sys.exit(-1)
		if validate_response(times, rsp_len, rsp) != True:
			print_err(PROTOCOL_TEST_HDR + "Response fail")
			sys.exit(-1)

		# dump_hex(rsp, "Response: ")
		end = int(round(time.time() * 1000))
		print "Send %d times, %.2gms" % (times, ((end-start)*1000))
		times += 1

