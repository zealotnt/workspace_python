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
	parser.add_option(  "-l",
						dest="loop",
						action="store_true",
						default=False)
	parser.add_option(  "-t", "--target",
						dest="target",
						default="RF",
						help="specify target to get version from, can be either (RF -- APP -- RF|APP)")
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, options.baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)
	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	sirius_system = SiriusAPISystem(comm)

	targets = options.target.split(',')

	while True:
		if "RF" in targets:
			# Enable debug print of RF processor
			sirius_system.RfDebugPrintEnable()
			sirius_system.GetSurisdkVersion()
			sirius_system.GetSuriblVersion()

		if "APP" in targets:
			sirius_system.GetXmsdkVersion()
			sirius_system.GetSvcVersion()

		if options.loop == False:
			break