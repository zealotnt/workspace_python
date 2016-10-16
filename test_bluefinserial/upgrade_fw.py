#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# send_cmd.py


# ---- IMPORTS

import os
import re
import time
import sys
import serial
import struct
from optparse import OptionParser, OptionGroup

sys.path.insert(0, 'bluefinserial')
from sirius_api_fw_upgrade import *
from datalink_deliver import *
from scan import scan
from utils import *

# ---- CONSTANTS
DEFAULT_APP_SVC_FILE = "/home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Service/svc.json.tar.xz"
DEFAULT_APP_FW_FILE = "/home/zealot/eclipseMars/workspace_Bluefin/BBB-AppDevelopment/testSerialBBB/Release-Board-Slave/xmsdk.json.tar.xz"
DEFAULT_RF_FW_FILE = "/home/zealot/workspace_test/surisdk_local/Debug_deploy/surisdk_local.json.tar.xz"
DEFAULT_RF_BL_FILE = "/home/zealot/miscTest/suribootloader/Debug_deploy/suribootloader.json.tar.xz"

if __name__ == "__main__":

	return_code = 0

	parser = OptionParser()

	parser.add_option(  "-s", "--serial",
						dest="serial",
						type="string",
						help="define the serial port to use")
	parser.add_option(  "-f", "--file",
						dest="firmware_file",
						type="string",
						help="define the file path to firmware")
	parser.add_option(  "-t", "--type",
						dest="firmware_type",
						type="string",
						help="define the firmware type to upgrade")
	(options, args) = parser.parse_args()

	if options.serial is not None:
		serial = options.serial
	else:
		serial = BLUEFINSERIAL_DEFAULT_SERIAL_PORT
		print_ok("No serial port specified, use " +
			BLUEFINSERIAL_DEFAULT_SERIAL_PORT +
			" with baudrate = " +
			str(BLUEFINSERIAL_BAUDRATE) +
			" as default")

	if options.firmware_type is None:
		print_err("Please specify firmware_type by -t or --type flag")
		sys.exit(-1)

	if options.firmware_type == "rf_fw":
		file = DEFAULT_RF_FW_FILE
	elif options.firmware_type == "rf_bl":
		file = DEFAULT_RF_BL_FILE
	elif options.firmware_type == "app_fw":
		file = DEFAULT_APP_FW_FILE
	elif options.firmware_type == "app_svc":
		file = DEFAULT_APP_SVC_FILE
	else:
		print_err("Invalid firmware_type")
		sys.exit(-2)

	if options.firmware_file is not None:
		file = options.firmware_file

	file_path = file
	port_name = serial
	file_type = options.firmware_type

	comm = BluefinserialSend(port_name, BLUEFINSERIAL_BAUDRATE)

	sirius_fw_upgrade = SiriusAPIFwUpgrade(comm)

	count = 0
	while True:
		sirius_fw_upgrade.UpgradeFirmware(file_type, file_path)
		count += 1
		print "Success %d times" % count

