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
	parser.add_option(  "-p", "--sam-slot",
						dest="sam_slot",
						type="string",
						help="define the SAM slot to test (required)")
	(options, args) = parser.parse_args()

	if options.sam_slot is None:
		parser.print_help()
		sys.exit(-1)

	try:
		comm = BluefinserialSend(options.serial, int(options.baud))
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))
	print_ok("Try activate SAM slot " + str(options.sam_slot))

	sirius_sam = SiriusAPISam(comm)
	sirius_sam.ActivateSam(int(options.sam_slot))
	sirius_sam.ExchangeAPDU(int(options.sam_slot), '\x00')
