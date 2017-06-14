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
from sirius_api_system import *
from datalink_deliver import *
from scan import scan
from utils import *

# ---- CONSTANTS
DEFAULT_APP_PRJ = os.environ["APP_PRJ"] if os.getenv("APP_PRJ", "") != "" else "/home/zealot/workspace_sirius/xmsdk/"
DEFAULT_RF_WORKSPACE = os.getenv("RF_PRJ", "") if os.getenv("RF_PRJ", "") != "" else "/home/zealot/workspace_sirius/"

supportFirmwareModels = {
	"rf_fw": {
		"GET_VER_FUNC": SiriusAPISystem.GetSurisdkVersion,
	},
	"rf_bl": {
		"GET_VER_FUNC": SiriusAPISystem.GetSuriblVersion,
	},
	"app_fw": {
		"GET_VER_FUNC": SiriusAPISystem.GetXmsdkVersion,
	},
	"app_svc": {
		"GET_VER_FUNC": SiriusAPISystem.GetSvcVersion,
	}
}

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
	parser.add_option(  "-f", "--file",
						dest="firmware_file",
						type="string",
						help="- define the file path to firmware \
						- note: user can export env_var APP_PRJ/RF_PRJ point to the project folder \
						- example:  export APP_PRJ=/home/zealot/workspace_sirius/xmsdk \
						- example2: export APP_PRJ=/home/zealot/workspace_sirius/surisdk")
	parser.add_option(  "-t", "--type",
						dest="firmware_type",
						type="string",
						help="define the firmware type to upgrade (%s)" % "/".join(list(supportFirmwareModels)))
	parser.add_option(  "-l", "--loop",
						dest="download_loop",
						action="store_true",
						default=False,
						help="choose upgrade operation to loop forever or not, default = False")

	(options, args) = parser.parse_args()

	if options.firmware_type not in supportFirmwareModels:
		print_err("Please specify firmware_type by -t or --type flag")
		parser.print_help()
		sys.exit(-1)
	upgradeModel = supportFirmwareModels[options.firmware_type]

	file = ProcessFilePath(options.firmware_file)

	ret = CompressFileWithExtension(".json", file)
	if ret != None:
		file = ret

	try:
		comm = BluefinserialSend(options.serial, options.baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Upgrade %s with %s" % (options.firmware_type, file))
	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))
	sirius_fw_upgrade = SiriusAPIFwUpgrade(comm)
	sirius_system = SiriusAPISystem(comm)

	count = 0
	# To execute at least 1 time, we give an or condition to (count == 0)
	# then, if it does not require looping, the program ends
	while True:
		if options.download_loop == False:
			curVer = upgradeModel["GET_VER_FUNC"](sirius_system)
			print("Before update, %s version = %s" % (options.firmware_type, curVer))

		if sirius_fw_upgrade.UpgradeFirmware(options.firmware_type, file) is False:
			print_err("Upgrade firmware fail, exit")
			sys.exit(-1)

		if options.download_loop == False:
			curVer = upgradeModel["GET_VER_FUNC"](sirius_system)
			print("After update, %s version = %s" % (options.firmware_type, curVer))
			break
		count += 1
		print "Success %d times" % count

