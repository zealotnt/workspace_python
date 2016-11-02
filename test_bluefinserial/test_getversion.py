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
						help="define the serial port to use")
	parser.add_option(  "-b", "--baud",
						dest="baud",
						type="string",
						help="define the serial baudrate to use")
	(options, args) = parser.parse_args()

	if options.serial is not None:
		port_name = options.serial
	else:
		port_name = BLUEFINSERIAL_DEFAULT_SERIAL_PORT
	if  options.baud is not None:
		port_baud = options.baud
	else:
		port_baud = BLUEFINSERIAL_BAUDRATE

	try:
		comm = BluefinserialSend(port_name, port_baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Use " + port_name + " with baudrate = " + str(port_baud))

	sirius_system = SiriusAPISystem(comm)
	sirius_system.GetXmsdkVersion()
	sirius_system.GetSvcVersion()
	sirius_system.GetSurisdkVersion()
	sirius_system.GetSuriblVersion()

