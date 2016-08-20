#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# send_cmd.py


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

VERBOSE = 0

AUTHOR = u"zealotnt"

VERSION = "0.0.1"

PROG = "send_cmd"

COPYRIGHT = u"Copyright © 2016"

DEFAULT_SERIAL_PORT = "/dev/rfcomm0"

# ---- GLOBALS

# ---- MAIN

if __name__ == "__main__":

	return_code = 0

	parser = OptionParser()

	parser.add_option(  "-s", "--serial", 
						dest="serial", 
						type="string", 
						help="define the serial port to use")
	parser.add_option(  "-v", "--verbose", 
						action="count", 
						dest="verbose", 
						help="enable verbose mode")
	parser.add_option(  "-l", "--list-serial", 
						action="store_true", 
						dest="list_serial", 
						default=False, 
						help="display available serial ports")

	(options, args) = parser.parse_args()

	if options.list_serial:
		print "Available serial ports:"
		for port_name in scan():
			print '  - ' + port_name
		sys.exit(0)

	if options.serial is not None:
		serial = options.serial
	else:
		serial = DEFAULT_SERIAL_PORT
		print_err("No serial port specified, use " + DEFAULT_SERIAL_PORT + " as default")

	port_name = serial

	if options.verbose >= VERBOSE:
		print 'Open serial port: ' + port_name
	comm = BluefinserialSend(port_name, 460800)

	pkt = BluefinserialCommand()
	cmd = pkt.Packet('\x8b', '\x00', '\x03')

	rsp = ''

	while True:
		dump_hex(cmd, "Command: ")
		start = time.clock()
		rsp = comm.Exchange(cmd)
		if rsp is not None:
			dump_hex(rsp, "Response: ")
		else:
			print_err("Transmit fail")
			sys.exit(-1)
		end = time.clock()
		print "%.2gms" % ((end-start)*1000)

