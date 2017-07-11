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
	parser.add_option(  "-p", "--sam-slot",
						dest="sam_slot",
						type="string",
						help="define the SAM slot to test (required)")
	parser.add_option(  "-l", "--loop",
						dest="run_loop",
						action="store_true",
						default=False,
						help="choose upgrade operation to loop forever or not, default = False")
	parser.add_option(  "-f", "--flow",
						dest="run_flow",
						default="0",
						help="choose run flow for SAM test\
						- flow=0: Loop[activate -> pps -> exchange -> deactivate]\
						- flow=1: activate -> pps -> Loop[exchange]")
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
	system_api = SiriusAPISystem(comm)
	sam_slot = int(options.sam_slot)

	# Enable debug print of RF processor
	system_api.RfDebugPrintEnable()

	# Let's see any debug print output
	system_api.GetSurisdkVersion()

	# Start stress testing
	if options.run_flow == "0":
		count = 0
		while (options.run_loop) or (count == 0):
			time.sleep(0.1)
			# To execute at least 1 time, we give an or condition to (count == 0)
			# then, if it does not require looping, the program ends
			ret = sirius_sam.ActivateSam(sam_slot)
			if ret is None:
				sys.exit(-1)

			# SAM0 - secure memory is PPS automatically
			ret = sirius_sam.PpsSam(sam_slot, PPSBaudrate.B115200)
			if (sam_slot is not 0) and (ret is None):
				sys.exit(-2)

			if sirius_sam.ExchangeAPDU(sam_slot, ExampleAPDU.SECURE_MEM_APDU_1) is None:
				sys.exit(-3)
			count += 1
			print "Success %d times" % count

			ret = sirius_sam.DeactivateSam(sam_slot)
			if ret is None:
				sys.exit(-2)
	elif options.run_flow == "1":
		# To execute at least 1 time, we give an or condition to (count == 0)
		# then, if it does not require looping, the program ends
		ret = sirius_sam.ActivateSam(sam_slot)
		if ret is None:
			sys.exit(-1)

		# SAM0 - secure memory is PPS automatically
		ret = sirius_sam.PpsSam(sam_slot, PPSBaudrate.B115200)
		if (sam_slot is not 0) and (ret is None):
			sys.exit(-2)

		count = 0
		while (options.run_loop) or (count == 0):
			if sirius_sam.ExchangeAPDU(sam_slot, ExampleAPDU.SECURE_MEM_APDU_1) is None:
				sys.exit(-3)
			count += 1
			print "Success %d times" % count
