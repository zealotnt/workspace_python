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
from sirius_api_system import *
from scan import scan
from utils import *

if __name__ == "__main__":

	parser = OptionParser()
	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						default=BLUEFINSERIAL_DEFAULT_SERIAL_PORT,
						help="define the serial port to use, default = " + BLUEFINSERIAL_DEFAULT_SERIAL_PORT)
	parser.add_option(  "-b", "--baud",
						dest="baud",
						type="string",
						default=BLUEFINSERIAL_BAUDRATE,
						help="define the serial baudrate to use, default = "+str(BLUEFINSERIAL_BAUDRATE))
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, options.baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)
	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	pkt = BluefinserialCommand(BluefinserialCommand.TARGET_RF)
	cmd = pkt.Packet('\x8b', '\x02', '\x01\x01\x02\x01\x00\x02\x01\xf4\x01')
	count = 1
	while True:
		rsp = comm.Exchange(cmd)
		dump_hex(rsp, "Trial %d response from RF (%d) bytes: " % (count, len(rsp)))
		count += 1