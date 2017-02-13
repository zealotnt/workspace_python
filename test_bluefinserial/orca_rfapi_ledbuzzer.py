#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# rfapi_setpassword.py


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
	parser.add_option(  "-v", "--verify",
						dest="verify_password",
						default="",
						help="password to verify with orcanfc board")
	parser.add_option(  "-p", "--pass",
						dest="new_password",
						default="",
						help="password to set to orcanfc board")
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	system_api = OrcaAPISystem(comm)

	if options.verify_password is None:
		print_err("Verify password is missing")
		parser.print_help()
		sys.exit(-1)
	elif options.verify_password and options.new_password:
		# Let's verify the root password
		system_api.OrcaRfApiUpdatePassword(options.verify_password, options.new_password)
	else:
		# Let's verify the root password
		system_api.OrcaRfApiVerifyPassword(options.verify_password)
