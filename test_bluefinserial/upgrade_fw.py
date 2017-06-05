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
import ntpath
from optparse import OptionParser, OptionGroup

sys.path.insert(0, 'bluefinserial')
from sirius_api_fw_upgrade import *
from datalink_deliver import *
from scan import scan
from utils import *

# ---- CONSTANTS
if os.getenv("APP_PRJ", "") != "":
	DEFAULT_APP_PRJ = os.environ["APP_PRJ"]
else:
	DEFAULT_APP_PRJ = "/home/zealot/workspace_sirius/xmsdk/"
DEFAULT_APP_SVC_FILE = DEFAULT_APP_PRJ + "/Release-Board-Service/svc.json.tar.xz"
DEFAULT_APP_FW_FILE = DEFAULT_APP_PRJ + "/Release-Board-Slave/xmsdk.json.tar.xz"

if os.getenv("RF_PRJ", "") != "":
	DEFAULT_RF_WORKSPACE = os.environ["RF_PRJ"]
else:
	DEFAULT_RF_WORKSPACE = "/home/zealot/workspace_sirius/"
DEFAULT_RF_FW_FILE = DEFAULT_RF_WORKSPACE + "/surisdk/Debug_deploy/surisdk.json.tar.xz"
DEFAULT_RF_BL_FILE = DEFAULT_RF_WORKSPACE + "/suribootloader/Debug_deploy/suribootloader.json.tar.xz"

TYPE_RF_FW = "rf_fw"
TYPE_RF_BL = "rf_bl"
TYPE_APP_FW = "app_fw"
TYPE_APP_SVC = "app_svc"

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
						help="define the firmware type to upgrade (%s/%s/%s/%s)" % (TYPE_APP_SVC, TYPE_APP_FW, TYPE_RF_BL, TYPE_RF_FW))
	parser.add_option(  "-l", "--loop",
						dest="download_loop",
						action="store_true",
						default=False,
						help="choose upgrade operation to loop forever or not, default = False")
	parser.add_option(  "-c", "--compress",
						dest="compressFile",
						action="store_true",
						default=False,
						help="this will try to compress the input file, default = False")

	(options, args) = parser.parse_args()

	if options.firmware_type is None:
		print_err("Please specify firmware_type by -t or --type flag")
		parser.print_help()
		sys.exit(-1)

	if options.firmware_type == TYPE_RF_FW:
		file = DEFAULT_RF_FW_FILE
	elif options.firmware_type == TYPE_RF_BL:
		file = DEFAULT_RF_BL_FILE
	elif options.firmware_type == TYPE_APP_FW:
		file = DEFAULT_APP_FW_FILE
	elif options.firmware_type == TYPE_APP_SVC:
		file = DEFAULT_APP_SVC_FILE
	else:
		print_err("Invalid firmware_type")
		parser.print_help()
		sys.exit(-2)

	file = ProcessFilePath(options.firmware_file)

	if options.compressFile is True:
		jsonExtension = ".json"
		jsonInputName = file
		if jsonInputName.endswith(jsonExtension):
			# strip the .json
			fileOutName = jsonInputName[:len(jsonInputName) - len(jsonExtension)] + ".tar.xz"
			tarCmd = "tar -cvf %s -C %s %s" % (fileOutName, os.path.dirname(jsonInputName), ntpath.basename(jsonInputName))
			print(tarCmd)
			# [Ref](http://stackoverflow.com/questions/18681595/tar-a-directory-but-dont-store-full-absolute-paths-in-the-archive)
			ret = os.system(tarCmd)
			if ret != 0:
				print_err("Compress file error, quit")
				sys.exit(-1)
			# update the `file` variable point to the generated file
			file = fileOutName
		else:
			print_err("Input file not .json, ignore compressing")

	try:
		comm = BluefinserialSend(options.serial, options.baud)
	except Exception, e:
		print e
		parser.print_help()
		sys.exit(-1)

	print_ok("Upgrade %s with %s" % (options.firmware_type, file))
	print_ok("Use " + options.serial + " with baudrate = " + str(options.baud))
	sirius_fw_upgrade = SiriusAPIFwUpgrade(comm)

	count = 0
	# To execute at least 1 time, we give an or condition to (count == 0)
	# then, if it does not require looping, the program ends
	while (options.download_loop) or (count == 0):
		sirius_fw_upgrade.UpgradeFirmware(options.firmware_type, file)
		count += 1
		print "Success %d times" % count

