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
	parser.add_option(  "-c", "--color",
						dest="color",
						type="string",
						default="",
						help="Specified to set R/G/B/O (red/green/blue/orange) led")
	parser.add_option(  "-t",
						dest="tunes",
						type="string",
						default="",
						help="Specified to set buzzer frequency")

	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	system_api = OrcaAPISystem(comm, verbose=True)

	if options.color != "":
		system_api.OrcaRfApiSetLed(MlsOrcaLeds.ParseString(options.color))
	if options.tunes != "":
		system_api.OrcaRfApiSetBuzzer(int(options.tunes))
