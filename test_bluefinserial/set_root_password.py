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
from sirius_api_sam import *
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
						help="define the serial baudrate to use, default = " + str(BLUEFINSERIAL_BAUDRATE))
	parser.add_option(  "-p", "--pass",
						dest="password",
						default="",
						help="password to set to root user")
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	sirius_sam = SiriusAPISam(comm)
	system_api = SiriusAPISystem(comm)

	# Let's set the root password
	system_api.SetRootPassword(options.password)
