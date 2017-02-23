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
	parser.add_option(  "-w", "--write",
						dest="enable_write",
						action="store_true",
						default=False,
						help="tell the script to write new value to Maxim")
	(options, args) = parser.parse_args()

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))

	system_api = OrcaAPISystem(comm, verbose=True)

	if options.enable_write:
		system_api.OrcaRfApiUpdateInfo(TID="80000106",
								   MID="1118000100",
								   STAN=21813,
								   APN="mptnet",
								   DEV_IP="1.2.3.4",
								   HOST="118.201.98.194",
								   PORT=19301)

	read_tags = ["TID", "MID", "STAN", "APN", "DEV_IP", "HOST", "PORT"]
	for tag in read_tags:
		system_api.OrcaRfApiReadInfo(tag)
