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

sys.path.insert(0, 'bluefinserial')
from datalink_deliver import *
from sirius_api_sam import *
from sirius_api_system import *
from orca_api_system import *
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
						help="define the serial baudrate to use, default = " + str(BLUEFINSERIAL_BAUDRATE))
	parser.add_option(  "-r", "--raw_file",
						dest="ca_raw_file_path",
						type="string",
						default="",
						help="specified to path of the raw ca_file (required)")
	parser.add_option(  "-f", "--header_file",
						dest="ca_header_file_path",
						type="string",
						default="",
						help="specified to path of the header ca_file (required)")
	parser.add_option(  "-n", "--array_name",
						dest="array_name",
						type="string",
						default="",
						help="specified to path of the array-name of header ca_file to parse (required)")
	parser.add_option(  "-d", "--debug",
						dest="debug_enable",
						action="store_true",
						default=False,
						help="turn debugging on")
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	if options.ca_raw_file_path is "" and options.ca_header_file_path is "":
		print_err("ca_raw_file_path/ca_raw_header_file_path is required")
		parser.print_help()
		sys.exit(-1)

	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	system_api = OrcaAPISystem(comm, verbose=True)

	if options.ca_raw_file_path != "":
		ret = system_api.OrcaRfApiUpdateCaCert(options.ca_raw_file_path, debug=options.debug_enable)

		if ret == True:
			system_api.OrcaRfApiVerifyCaCert(options.ca_raw_file_path)

	if options.ca_header_file_path != "":
		if options.array_name == "":
			print_err("Array name is required")
			parser.print_help()
			sys.exit(-1)
		ret = system_api.OrcaRfApiUpdateCaCertFromHeader(options.ca_header_file_path, options.array_name, debug=options.debug_enable)

		if ret == True:
			system_api.OrcaRfApiVerifyCaCertFromHeader(options.ca_header_file_path, options.array_name)
