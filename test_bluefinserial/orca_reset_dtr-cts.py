#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rfapi_updateinfo.py


# ---- IMPORTS
import os
import re
import time
import sys
import serial
import struct
from optparse import OptionParser, OptionGroup

BLUEFINSERIAL_DEFAULT_SERIAL_PORT = "/dev/ttyNFC"

if __name__ == "__main__":

	parser = OptionParser()

	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						default=BLUEFINSERIAL_DEFAULT_SERIAL_PORT,
						help="define the serial port to use, default = " + BLUEFINSERIAL_DEFAULT_SERIAL_PORT)
	parser.add_option(  "-i", "--invert",
						dest="invert_logic",
						action="store_true",
						default=False,
						help="This will set the RTS to low, DTR to high instead.")
	(options, args) = parser.parse_args()

	try:
		serial = serial.Serial(port=options.serial, baudrate=921600)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	if options.invert_logic == True:
		print("Pull RTS low, DTR high")
		serial.setRTS(True)
		serial.setDTR(False)
	else:
		print("Pull RTS high, DTR low")
		serial.setRTS(False)
		serial.setDTR(True)

	time.sleep(0.5)
	# Pull two pin low
	serial.setRTS(True)
	serial.setDTR(True)
	print("Pull DTR/RTS low")
