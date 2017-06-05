#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-05-08 13:12:35

import mlsFwPack
import sys
import os
import re
import time
import serial
import struct
import ntpath
from optparse import OptionParser, OptionGroup

TYPE_RF_FW = "rf_fw"
TYPE_RF_BL = "rf_bl"
TYPE_APP_FW = "app_fw"
TYPE_APP_SVC = "app_svc"

jsonPrefixDict = {
	TYPE_RF_BL: "suribl",
	TYPE_RF_FW: "surisdk",
	TYPE_APP_SVC: "svc",
	TYPE_APP_FW: "xmsdk",
}

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def print_err(text):
	print >> sys.stderr, bcolors.FAIL + text + bcolors.ENDC

def remoteFileProtocolPrefix(path):
	fileProtocolPrefix = "file:///"
	file = path
	if file.startswith(fileProtocolPrefix):
		file = file[len(fileProtocolPrefix)-1:]
	return file

def main():
	parser = OptionParser()
	parser.add_option(  "-f", "--file",
						dest="firmwareFile",
						type="string",
						help="- define the file path to firmware")
	parser.add_option(  "-o", "--version-object",
						dest="firmwareVerFile",
						type="string",
						help="- define the file path to firmware version object built")
	parser.add_option(  "-t", "--type",
						dest="firmwareType",
						type="string",
						help="define the firmware type to upgrade (%s/%s/%s/%s)" % (TYPE_APP_SVC, TYPE_APP_FW, TYPE_RF_BL, TYPE_RF_FW))
	parser.add_option(  "-v", "--firmware-ver",
						dest="firmwareVerVal",
						type="string",
						help="hardcode the firmware version to put to json file")
	parser.add_option(  "-c", "--compress",
						dest="compressFile",
						action="store_true",
						default=False,
						help="this will try to compress the input file, default = False")

	(options, args) = parser.parse_args()

	if options.firmwareType is None:
		print_err("firmware type is missing")
		parser.print_help()
		sys.exit(-1)
	if options.firmwareFile is None:
		print_err("firmware file is missing")
		parser.print_help()
		sys.exit(-1)
	if (options.firmwareVerVal is None) and (options.firmwareVerFile is None):
		print_err("firmware version is missing")
		parser.print_help()
		sys.exit(-1)
	if options.firmwareFile is not None:
		file = remoteFileProtocolPrefix(options.firmwareFile)
	if options.firmwareVerFile is not None:
		options.firmwareVerFile = remoteFileProtocolPrefix(options.firmwareVerFile)

	# Get version value
	if options.firmwareVerFile:
		fwMetadata = mlsFwPack.getRodata(options.firmwareVerFile)
	else:
		fwMetadata = options.firmwareVerVal

	# Get binary value of firmware
	fwBinary = open(file, 'rb').read()

	# Create the json file
	fwJson = mlsFwPack.packJson(jsonPrefixDict[options.firmwareType], fwMetadata, fwBinary)
	fwExtension = ".bin"
	if file.endswith(fwExtension):
		pathOutput = file[:len(file) - len(fwExtension)] + ".json"
		# The output file will created in same folder of the caller
		pathOutput = ntpath.basename(pathOutput)
	else:
		pathOutput = "out.json"
	mlsFwPack.writeJsonFile(pathOutput, fwJson)
	print("Write successfully to " + pathOutput)

if __name__ == "__main__":
	main()
