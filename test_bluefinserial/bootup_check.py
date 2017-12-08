#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# bootup_check.py


# ---- IMPORTS
import os
import re
import time
import sys
import subprocess
import json
import base64
import md5
import threading
import logging
import datetime
import traceback
from logging.handlers import RotatingFileHandler

# ---- CONSTANTS
FILE_PRESENT 				= 0
FILE_ABSENT 				= 1

def print_warn(text, fileLog=True):
	print_text = SCRIPT_PREFIX("WARN", bcolors.WARNING) + text
	print(print_text)
	if fileLog == True:
		gLogger.warn(print_text)

def print_debug(text, fileLog=True):
	print_text = SCRIPT_PREFIX("DEBUG") + text
	print(print_text)
	if fileLog == True:
		gLogger.debug(print_text)

def print_noti(text, fileLog=True):
	print_text = SCRIPT_PREFIX("INFO", bcolors.OKYEL) + text
	print(print_text)
	if fileLog == True:
		gLogger.info(print_text)

def print_err(text, fileLog=True):
	print_text = SCRIPT_PREFIX("ERR", bcolors.FAIL) + text
	print(print_text)
	if fileLog == True:
		gLogger.err(print_text)

def print_ok(text, fileLog=True):
	print_text = SCRIPT_PREFIX("INFO_OK", bcolors.OKGREEN) + text
	print(print_text)
	if fileLog == True:
		gLogger.info(print_text)

def SCRIPT_PREFIX(debugType="", color=""):
	return "[%sBOOTUP_%s%s] " % (color, debugType, bcolors.ENDC)

# ---- GLOBALS
class SiriusFirmwareRecovery():
	FIRMWARE_BASE_BACKUP_FOLDER		= "/home/root/fw_backup/"
	FACTORY_FOLDER 					= FIRMWARE_BASE_BACKUP_FOLDER + "factory/"
	BASELINE_FOLDER					= FIRMWARE_BASE_BACKUP_FOLDER + "baseline/"
	BACKUP_FOLDER					= FIRMWARE_BASE_BACKUP_FOLDER + "backup/"

	FIRMWARE_UPGRADING_FLAG 	= FIRMWARE_BASE_BACKUP_FOLDER + "upg_flag"

	SURI_ERASER_NAME			= "eraser.json.tar.xz"
	SURIBL_FW_FILE_NAME			= "suribootloader.json.tar.xz"
	SURISDK_FW_FILE_NAME		= "surisdk.json.tar.xz"
	PN5180_FW_FILE_NAME			= "pn5180.json.tar.xz"
	EMV_CONF0_FILE_NAME			= "emvConf0.tar.xz"
	EMV_CONF1_FILE_NAME			= "emvConf1.tar.xz"
	EMV_CONF2_FILE_NAME			= "emvConf2.tar.xz"
	EMV_CONF3_FILE_NAME			= "emvConf3.tar.xz"
	EMV_CAPK_FILE_NAME			= "emvCapk.tar.xz"
	SVC_FW_FILE_NAME			= "svc.json.tar.xz"
	XMSDK_FW_FILE_NAME			= "xmsdk.json.tar.xz"

	@staticmethod
	def FirmwareAccessOrder():
		return [
			"ERASER",
			"SURIBL",
			"SVC",
			"SURISDK",
			"PN5180",
			"EMV_CONF0",
			"EMV_CONF1",
			"EMV_CONF2",
			"EMV_CONF3",
			"EMV_CAPK",
			"XMSDK"
		]

	@staticmethod
	def FirmwareRecoveryModels(inFolder):
		return {
			"ERASER": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeSuribl,
				"FIRMWARE_FILE": SiriusFirmwareRecovery.FACTORY_FOLDER + SiriusFirmwareRecovery.SURI_ERASER_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "suribl",
				"BINARY_FILE": "eraser.tar.xz",
				"ACTION_NAME": "Erase RF Processor flash memory",
				"FILE_USED": "BINARY",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"SURIBL": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeSuribl,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.SURIBL_FW_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "suribl",
				"BINARY_FILE": "suribl.tar.xz",
				"ACTION_NAME": "Recovery suri bootloader",
				"FILE_USED": "BINARY",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"SURISDK": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeSurisdk,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.SURISDK_FW_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "surisdk",
				"BINARY_FILE": "surisdk.bin",
				"ACTION_NAME": "Recovery surisdk",
				"FILE_USED": "BINARY",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"PN5180": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradePn5180,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.PN5180_FW_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": SiriusFwRecoveryExecuter.Pn5180AntennaGet,
				"JSON_PREFIX": "pn5180",
				"BINARY_FILE": "pn5180.bin",
				"ACTION_NAME": "Recovery pn5180 firmware",
				"FILE_USED": "COMPRESSED",
				"MAX_RETRY_TIMES": 5,
				"RETRY_DELAY": 10,
			},
			"EMV_CONF0": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeEmv,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.EMV_CONF0_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "",
				"BINARY_FILE": "",
				"ACTION_NAME": "Recovery emvConf0",
				"FILE_USED": "JSON",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"EMV_CONF1": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeEmv,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.EMV_CONF1_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "",
				"BINARY_FILE": "",
				"ACTION_NAME": "Recovery emvConf1",
				"FILE_USED": "JSON",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"EMV_CONF2": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeEmv,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.EMV_CONF2_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "",
				"BINARY_FILE": "",
				"ACTION_NAME": "Recovery emvConf2",
				"FILE_USED": "JSON",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"EMV_CONF3": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeEmv,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.EMV_CONF3_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "",
				"BINARY_FILE": "",
				"ACTION_NAME": "Recovery emvConf3",
				"FILE_USED": "JSON",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"EMV_CAPK": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.UpgradeEmv,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.EMV_CAPK_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "",
				"BINARY_FILE": "",
				"ACTION_NAME": "Recovery emvCapk",
				"FILE_USED": "JSON",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"SVC": {
				"UPG_FUNC": SiriusFwRecoveryExecuter.RunSvc,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.SVC_FW_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "svc",
				"BINARY_FILE": "svc",
				"ACTION_NAME": "",
				"FILE_USED": "BINARY",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
			"XMSDK": {
				"UPG_FUNC": None,
				"FIRMWARE_FILE": inFolder + SiriusFirmwareRecovery.XMSDK_FW_FILE_NAME,
				"EXTRA_INFO_EXTRACT_FUNC": None,
				"JSON_PREFIX": "xmsdk",
				"BINARY_FILE": "xmsdk",
				"ACTION_NAME": "",
				"FILE_USED": "BINARY",
				"MAX_RETRY_TIMES": 0,
				"RETRY_DELAY": 0,
			},
		}

	@staticmethod
	def RecoveryFlowModel(fwInFolder, curFolderName, nextFolderName, tearDownFunc=None):
		fwAccess = SiriusFirmwareRecovery.FirmwareAccessOrder()
		modelsDict = SiriusFirmwareRecovery.FirmwareRecoveryModels(fwInFolder)
		modelsArray = []
		for idx, accessName in enumerate(fwAccess):
			modelsArray.append(modelsDict[accessName])

		return {
			"FW_IN_FOLDER": fwInFolder,
			"FW_RECOVERY_MODELS": modelsArray,
			"NEXT_FOLDER_NAME": nextFolderName,
			"CUR_FOLDER_NAME": curFolderName,
			"TEAR_DOWN_FUNC": tearDownFunc,
		}

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	OKYEL = '\033[33m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

class FileLogging():
	LOG_FILE_NAME				= "bootup_check.log"
	LOG_FILE_PATH				= SiriusFirmwareRecovery.FIRMWARE_BASE_BACKUP_FOLDER + LOG_FILE_NAME
	LOG_MODULE_NAME				= "bootup_check"
	LOG_FILE_MAX_NUM			= 5
	LOG_FILE_MAX_SIZE			= 10*1024 # 10KB

	def __init__(self,
				name=None,
				logFilePath=None,
				maxBytes=None,
				backupCount=None):
		"""
		Creates a rotating log
		"""
		if name is None:
			name=self.LOG_MODULE_NAME
		if logFilePath is None:
			logFilePath = self.LOG_FILE_PATH
		if maxBytes is None:
			maxBytes = self.LOG_FILE_MAX_SIZE
		if backupCount is None:
			backupCount = self.LOG_FILE_MAX_NUM

		self.logger = logging.getLogger(name)
		self.logger.setLevel(logging.DEBUG)

		# add a rotating handler
		self.handler = RotatingFileHandler(logFilePath, maxBytes=maxBytes, backupCount=backupCount)
		self.logger.addHandler(self.handler)

	def debug(self, text):
		self.logger.debug(text)

	def info(self, text):
		self.logger.info(text)

	def warn(self, text):
		self.logger.warn(text)

	def err(self, text):
		self.logger.error(text)

# Create a global file logging object
gLogger = FileLogging()

class BlinkLedThread(threading.Thread):
	SYSFS_GPIO_VALUE_HIGH = '1'
	SYSFS_GPIO_VALUE_LOW = '0'

	def __init__(self, name):
		threading.Thread.__init__(self)
		self.name = name
		self.shouldKilled = False

	def run(self):
		print "Starting " + self.name
		self.BlinkLed()
		print "Exiting " + self.name

	def SetLedColor(self, value):
		if (value & 0x01):
			self.f_red.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_red.write(self.SYSFS_GPIO_VALUE_LOW)

		if (value & 0x02):
			self.f_green.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_green.write(self.SYSFS_GPIO_VALUE_LOW)

		if (value & 0x04):
			self.f_blue.write(self.SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_blue.write(self.SYSFS_GPIO_VALUE_LOW)

		self.f_red.seek(0)
		self.f_green.seek(0)
		self.f_blue.seek(0)

	def BlinkLed(self):
		LED_RED = 150
		LED_GREEN = 151
		LED_BLUE = 152

		color_list = [0, 1, 2, 3, 4, 5, 6, 7]

		# Export gpio
		os.system("echo 150 > /sys/class/gpio/export")
		os.system("echo 151 > /sys/class/gpio/export")
		os.system("echo 152 > /sys/class/gpio/export")

		# Set output
		os.system("echo out > /sys/class/gpio/gpio150/direction")
		os.system("echo out > /sys/class/gpio/gpio151/direction")
		os.system("echo out > /sys/class/gpio/gpio152/direction")

		self.f_red = open("/sys/class/gpio/gpio150/value", "r+")
		self.f_green = open("/sys/class/gpio/gpio151/value", "r+")
		self.f_blue = open("/sys/class/gpio/gpio152/value", "r+")

		while self.shouldKilled == False:
			for color in color_list:
				self.SetLedColor(color)
				time.sleep(0.1)

	def StopThread(self):
		self.shouldKilled = True

class SiriusFwValidator():

	@staticmethod
	def Extractfile(file_path):
		tarExamineCmd = "bsdtar -tf " + file_path
		pListFile = subprocess.Popen(['bsdtar', '-tf', file_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = pListFile.communicate()
		rc = pListFile.returncode

		tarCmd = "bsdtar -xf " + file_path
		rc = os.system(tarCmd)
		if rc != 0:
			print_err("err when extracting file " + file_path)
			return None
		return output

	@staticmethod
	def DecodeJsonAndWriteToFile(json_file, json_prefix, binary_out_name, extra_info_extract_func, dry_run=False):
		json_file_name = json_file.replace("\r", "").replace("\n", "")

		try:
			json_text = open(json_file[:len(json_file)-1], 'rb').read()
			json_decoded = json.loads(json_text)
		except Exception as e:
			raise Exception("Json decode file \"%s\" error: %s" % (json_file_name, str(e.message)))

		# if this firmware is pn5180 firmware (the json firmware is array)
		# no needd to process, the upgrade function will do it for us
		if isinstance(json_decoded, list):
			return True, json_file_name, "", []

		fw_dict = {key: value for (key, value) in (json_decoded.items())}
		if dry_run == False and json_prefix != "":
			print_debug(json_prefix + "'s md5 =" + fw_dict[json_prefix + "_md5"])
			print_debug(json_prefix + "'s metadata =" + fw_dict[json_prefix + "_metadata"])

		# Emvconf don't follow the format, so if `json_prefix` is empty, bypass the md5 and base64 checking
		# The emv upgrader will check for us
		if json_prefix != "":
			json_md5 = fw_dict[json_prefix + "_md5"]
			json_based64 = fw_dict[json_prefix + "_fw"]
			try:
				json_binary = base64.standard_b64decode(json_based64)
			except Exception as e:
				raise Exception("Base64 decode file \"%s\" error: %s" % (json_file_name, str(e.message)))
			try:
				fileMd5 = md5.new()
				fileMd5.update(json_binary)
				md5_calculated = fileMd5.hexdigest()
			except Exception as e:
				raise Exception("MD5 calculated file \"%s\" error: %s" % (json_file_name, str(e.message)))

			# Check md5
			if md5_calculated != json_md5:
				print_err('Json: %s\'s md5 is not equal to calculated value\n\tCalculated: %s\n\tJson value: %s)' % (json_file_name, md5_calculated, json_md5))
				raise Exception('Json: %s\'s md5 is not equal to calculated value' % json_file_name)

		extra_info = None
		if extra_info_extract_func != None:
			extra_info = extra_info_extract_func(fw_dict)

		# if it is only for validating, no need to write to file
		if dry_run == True:
			return True, json_file_name, "", extra_info

		# Emvconf don't follow the format, so if `json_prefix` is empty, don't write the binary to file
		# The emv upgrader use the json directly
		if (json_prefix == "") or (binary_out_name == ""):
			return True, json_file_name, "", extra_info
		else:
			# write the content of json-based64-encoded data to a `binary_out_name`
			try:
				fh = open(binary_out_name, 'wb')
				fh.write(json_binary)
				fh.close()

				os.chmod(binary_out_name, 0777)
			except Exception as e:
				raise Exception("Write result file \"%s\" from \"%s\" err: %s" % (binary_out_name, json_file_name, str(e.message)))

		print_ok("Restore binary file \"%s\" ok" % (json_file_name))
		return True, json_file_name, binary_out_name, extra_info

	@staticmethod
	def CheckFilePresence(file_path):
		if os.path.isfile(file_path) is not True:
			return FILE_ABSENT
		return FILE_PRESENT

	@staticmethod
	def RestoreJsonFromCompressed(file_compressed, json_prefix, binary_out_name, extra_info_extract_func=None, dry_run=False):
		"""
		:param file_compressed: compress file to restore from
		:param json_prefix: the prefix of json in the firmware, and the output firmware
		:param dry_run: if true, the output file will be created. Otherwise, it won't

		:return: valid(bool), filename(string)
		"""

		# Try to restore
		if os.path.isfile(file_compressed) is not True:
			print_warn("Firmware \"%s\" backup not found" % (file_compressed))
			raise Exception("File %s not found" % (file_compressed))

		# Extract tar file
		extracted_file = SiriusFwValidator.Extractfile(file_compressed)
		if extracted_file is None:
			raise Exception("Can\'t extract %s" % file_compressed)

		# Decode json file
		return SiriusFwValidator.DecodeJsonAndWriteToFile(extracted_file, json_prefix, binary_out_name, extra_info_extract_func, dry_run)

	@staticmethod
	def IsScpFolderValid(extract_result):
		folder_name = ""
		idx = 0
		for line in extract_result.splitlines():
			match = re.search(r'^(\w+[^/])', line)
			if match:
				# First match, this will be the "based" folder
				if idx == 0:
					folder_name = match.group()
				# If there is other file/folder in this compress file, exit
				if match.group() != folder_name:
					return False, ""
			else:
				# Not match, return right away
				return False, ""
		return True, folder_name

	@staticmethod
	def Md5sumFileValidate(inFolder):
		cmd = ("cd %s && "
		"find *.tar.xz -type f -exec md5sum \{\} \\; | "
		"sort -k 2 | "
		"md5sum > /tmp/md5sum.all.sum && "
		"cmp /tmp/md5sum.all.sum md5sum.all.sum" % (inFolder))
		print_debug (cmd)
		return True if os.system(cmd) == 0 else False

	@staticmethod
	def Md5sumFileValidateOld(modelsArray, inFolder):
		md5SumAllFilePath = inFolder + "md5sum.all.sum"
		if os.path.isfile(md5SumAllFilePath) is not True:
			return False

		f = open(md5SumAllFilePath, 'rU')
		md5sumContent = f.read()
		f.close()

		def GetFilenameChecksumList(content):
			ret = []
			match = re.findall(r'^(.+)\s+[/\w\.]+/([\w\.\d]+)$', content, re.MULTILINE)
			for item in match:
				model = {
					"FILE_NAME": "",
					"FILE_CHK_SUM": ""
				}

				model["FILE_NAME"] = item[1]
				model["FILE_CHK_SUM"] = item[0]
				ret.append(model)
			if ret == []:
				return None
			return ret

		def GetFilenameChecksumFromModelsArray(modelsArray):
			ret = []
			for model in modelsArray:
				if os.path.isfile(model["FIRMWARE_FILE"]) is not True:
					print ("Not found: ", model["FIRMWARE_FILE"])
					return None
				f=open(model["FIRMWARE_FILE"], 'rb')
				fw_binary=f.read()
				f.close()
				fileMd5 = md5.new()
				fileMd5.update(fw_binary)
				md5_calculated = fileMd5.hexdigest()
				retModel = {
					"FILE_NAME": os.path.basename(model["FIRMWARE_FILE"]),
					"FILE_CHK_SUM": md5_calculated
				}
				ret.append(retModel)
			return ret

		retFromFile = GetFilenameChecksumList(md5sumContent)
		retFromModel = GetFilenameChecksumFromModelsArray(modelsArray)
		if retFromFile is None or retFromModel is None:
			print ("ret: ", retFromFile, retFromModel)
			print (1)
			return False
		# retFromFile could have more item than retFromModel
		# because sometimes, there is additional entry of the md5sumAllFw.sum itself
		if len(retFromFile) < len(retFromModel):
			print ("Len: ", len(retFromFile), len(retFromModel))
			print (2)
			return False

		matchItem = 0
		missing = []
		for idx, item in enumerate(retFromModel):
			found = False
			for idx2, item2 in enumerate(retFromFile):
				if item2["FILE_NAME"].lower().rstrip() == item["FILE_NAME"].lower().rstrip():
					if item2["FILE_CHK_SUM"].lower().rstrip() == item["FILE_CHK_SUM"].lower().rstrip():
						print("Pass!!! Sum:%s File: %s" % (item2["FILE_CHK_SUM"], item2["FILE_NAME"]))
						matchItem += 1
						found = True
			if found == False:
				missing.append(item["FILE_NAME"].lower().rstrip())

		if matchItem != len(retFromModel):
			print_warn("Not enough md5sumAllFw.sum matching\n\tWant:%d\n\tHave:%d\n\tMissing: %s" %
				(len(retFromModel), matchItem, "\n\t\t ".join(missing))
			)
			return False
		else:
			return True

	@staticmethod
	def ValidateFirmware(modelsArray, inFolder):
		# This function will validate the `md5sumAllFw.sum` with the files in `modelsArray`
		if SiriusFwValidator.Md5sumFileValidate(inFolder) != True:
			print_warn("Md5sumFileValidate() err in %s" % inFolder)
			return False
		print_noti("Md5sumFileValidate() ok in %s" % inFolder)

		# This loop will check the content inside the files (try extract, try check md5sum binary) in `modelsArray`
		present = 0
		for idx, model in enumerate(modelsArray):
			try:
				# we don't validate emv*.tar.xz firmware
				if model["JSON_PREFIX"] == "":
					continue

				# check validity of model in folder
				ret, jsonOut, binOut, extraInfo = SiriusFwValidator.RestoreJsonFromCompressed(model["FIRMWARE_FILE"],
																				   model["JSON_PREFIX"],
																				   model["BINARY_FILE"],
																				   model["EXTRA_INFO_EXTRACT_FUNC"],
																				   dry_run=True)
				if ret != True:
					print_err("Err when extract file")
				present += 1
			except Exception as e:
				err_msg = e.message
				if "not found" in err_msg:
					continue
				else:
					print_err(str(err_msg))
					print(traceback.format_exc())
					return False
		# This avoid case there is no upgrades firmware, but return True
		# => The main code will print no file present again => confused
		# => If no file present, just use the factory firmware
		if present != 0:
			return True
		else:
			return False

class SiriusFwRecoveryExecuter():
	@staticmethod
	def Pn5180AntennaGet(fw_dict):
		return {
			"pn5180_id": fw_dict["pn5180_id"],
			"pn5180_connection": fw_dict["pn5180_connection"],
		}

	@staticmethod
	def UpgradeSuribl(compress_file, extraInfo):
		SEND_SCP_SCRIPT 			= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/sendscp_mod.sh"
		RF_SCP_EXTRACT_PATH 		= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/buildSCP/rf_fw/"
		SEND_SCP_UART_PORT 			= "/dev/ttymxc3"

		# Clean the old bootloader firmware folder
		os.system("rm -rf %s" % (RF_SCP_EXTRACT_PATH))
		os.system("mkdir -p %s" % (RF_SCP_EXTRACT_PATH))

		# detect the content of SCP bootloader firmware
		tarExamineCmd = "bsdtar -tf " + compress_file
		pListFile = subprocess.Popen(['bsdtar', '-tf', compress_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = pListFile.communicate()
		rc = pListFile.returncode
		ret, folder_name = SiriusFwValidator.IsScpFolderValid(output)
		if ret != True:
			print_err("Content in suribl is not valid !!!")
			return False

		# now, extract the firmware
		tarCmd = "bsdtar -xf " + compress_file + " -C " + RF_SCP_EXTRACT_PATH
		rc = os.system(tarCmd)
		if rc != 0:
			print_err("err when extracting file " + compress_file)
			return None

		# append RF_SCP_EXTRACT_PATH to folder_name to get absolute path
		rf_bl_folder = RF_SCP_EXTRACT_PATH + folder_name
		scpCmd = "bash " + SEND_SCP_SCRIPT + " " + SEND_SCP_UART_PORT + " " + rf_bl_folder + " y"
		# and upgrade...
		rc = os.system(scpCmd)
		if rc != 0:
			print_err("err when using SCP session")
			return None

		return True

	@staticmethod
	def KillSvcXmsdk():
		os.system("killall xmsdk")
		os.system("killall svc")

	@staticmethod
	def RunSvc(file_path, extraInfo):
		ret = os.system("./" + file_path + " &")
		if ret == 0:
			time.sleep(0.5)
			return True
		else:
			return False

	@staticmethod
	def UpgradeSurisdk(file_path, extraInfo):
		return True if os.system("/home/root/rfp_fwupgrade " + file_path) == 0 else False

	@staticmethod
	def UpgradePn5180(filePath, extraInfo):
		upg_cmd = "/home/root/pn5180/pn5180MutipleUpgradeApp %s" % (filePath)
		print(upg_cmd)
		ret = os.system(upg_cmd)
		if ret == 0:
			return True
		else:
			print_warn("pn5180 ret = %d" % ret)
			return False

	@staticmethod
	def UpgradeEmv(file_path, extraInfo):
		"""
		This function is used to upgrade emvconf0-3 or emvcapk
		"""
		return True if os.system("/home/root/emv/emv_upgrade_config_json " + file_path) == 0 else False

	@staticmethod
	def RecoveryFirmware(modelsArray, firmwareName):
		"""
		modelsArray should be the array which contains a dictionary:

		return 0 on success, others on error
		"""
		print_noti("Going to rollback using \"%s firmwares\"" % (firmwareName))
		output_json_filename = []
		output_bin_filename = []
		output_extra_info = []

		for idx, model in enumerate(modelsArray):
			if SiriusFwValidator.CheckFilePresence(model["FIRMWARE_FILE"]) != FILE_PRESENT:
				print_err("Firmware %s missing" % model["FIRMWARE_FILE"])
				return -1

		SiriusFwRecoveryExecuter.KillSvcXmsdk()

		########################################################################
		# Step 1
		# Extract firmware from list of compressed files
		for idx, model in enumerate(modelsArray):
			if model["JSON_PREFIX"] != "":
				print_noti("Step1-%d: Going to restore \"%s\" from \"%s\"" % (idx+1, model["JSON_PREFIX"], model["FIRMWARE_FILE"]))
			else:
				print_noti("Step1-%d: Going to extract from file \"%s\"" % (idx+1, model["FIRMWARE_FILE"]))

			ret, outJsonName, outBinName, extraInfo = SiriusFwValidator.RestoreJsonFromCompressed(
				model["FIRMWARE_FILE"],
				model["JSON_PREFIX"],
				model["BINARY_FILE"],
				model["EXTRA_INFO_EXTRACT_FUNC"]
			)
			output_json_filename.append(outJsonName)
			output_bin_filename.append(outBinName)
			output_extra_info.append(extraInfo)
			if ret != True:
				print_err("Err when extract %s" % model["FIRMWARE_FILE"])
				return -1

		########################################################################
		# Step 2
		# Start roll back the firmware one by one
		for idx, model in enumerate(modelsArray):
			maxRetryTimes = model["MAX_RETRY_TIMES"]
			print_noti("Step2-%d: Going to %s using \"%s\"" % (idx+1, model["ACTION_NAME"], model["FIRMWARE_FILE"]))

			while True:
				if model["UPG_FUNC"] is None:
					print_noti("Ignore firmware %s cause null upgrade handler" % model["FIRMWARE_FILE"])
					break # go to next firmware

				if model["FILE_USED"] == "BINARY":
					ret = model["UPG_FUNC"](output_bin_filename[idx], output_extra_info[idx])
				elif model["FILE_USED"] == "JSON":
					ret = model["UPG_FUNC"](output_json_filename[idx], output_extra_info[idx])
				elif model["FILE_USED"] == "COMPRESSED":
					ret = model["UPG_FUNC"](model["FIRMWARE_FILE"], output_extra_info[idx])
				else:
					raise Exception("Unregcognize FILE_USED: %s for firmware: %s" % (model["FILE_USED"], model["FIRMWARE_FILE"]))

				if ret != True:
					if maxRetryTimes > 0:
						maxRetryTimes -= 1
						print_noti("Fail when %s, wait for %ds then retrying, %d times left" % (model["ACTION_NAME"], model["RETRY_DELAY"], maxRetryTimes))
						time.sleep(model["RETRY_DELAY"])
						continue # retry
					print_err("Err when %s" % model["ACTION_NAME"])
					return -1 # error => return right away

				print_ok("%s using \"%s\" successfully" % (model["ACTION_NAME"], model["FIRMWARE_FILE"]))
				break # go to next firmware

		########################################################################
		# Step 3
		# Clean up everything
		for json_file in output_json_filename:
			if SiriusFwValidator.CheckFilePresence(json_file) == FILE_PRESENT:
				os.remove(json_file)
		for bin_file in output_bin_filename:
			# Just a temp solution for not accidential remove svc and xmsdk
			if "svc" in bin_file:
				continue
			if "xmsdk" in bin_file:
				continue
			if SiriusFwValidator.CheckFilePresence(bin_file) == FILE_PRESENT:
				os.remove(bin_file)

		SiriusFwRecoveryExecuter.KillSvcXmsdk()
		print_ok("Rollback using \"%s firmwares\" successfully" % (firmwareName))
		return 0

# ---- MAIN
def main():
	"""
	Some notes need to verify this feature:

	**Preparation:
	- A set of firmware (svc, xmsdk, surisdk, suribl) that has version different than the default flasher firmware, then upgrade them to board
	- A ftdi to access the console of A9 processsor, cause we need to type command to it

	**Test cases
	1. Only factory firmwares present -> need to roll back to factory firmwares
	2. All upgrade firmwares present, and the upgrades firmwares are valid -> need to roll back to ugprade firmwares
	3. Some of upgrade firmwares present -> need to catch the missing firmwares from factory
	4. Some of upgrade firmwares are corrupted -> need to use the factory firmwares
	+ compressed file corrupted
	+ json format invalid
	+ md5 mismatch
	+ base64 decode error

	**How to do it
	- 1,2,3,4: for verification of rollback to the right firmware, use the get version API to check the version of the firmware after roll back
	- In test case 1, can temporary rename the `upgrades folder`
	+ why? to force the `bootup_check.py` roll back with the factory firmwares version, cause it can't find any upgrade firmwares
	+ ex: `mv fw_backup/upgrades fw_backup/up`
	- In test case 3, can temporary rename any firmware from the `upgrades folder`, so the renamed firmwares will be replaced by the factory firmwares.
	- In test case 4, need to extract the firmware, modify its content, then compress it again.
	+ Why? because the only the valid firmware can be stored in "fw_backup/upgrades" folder (xmsdk logic)
	+ the firmware is corrupted because of some magical reason (emmc corrupt, others application mess up with the upgrades firmware, bug in xmsdk...)
	+ to extract the firmware, ex: "svc.json.tar.xz", use this command: `bsdtar -xvf svc.json.tar.xz`
	+ to compress it back, use this command: `bsdtar --xz -cvf svc.json.tar.xz Release-Board-Service/svc.json`
	"""
	if os.path.isfile(SiriusFirmwareRecovery.FIRMWARE_UPGRADING_FLAG) == False:
		print_ok("Bootup check ok", False)
		return

	# If firmware_upgrading_flag file is present, rollback for all
	blink_led = BlinkLedThread("Led blinker")
	blink_led.start()
	retVal = -1
	try:
		print_noti(">"*70)
		time_now = datetime.datetime.now()
		print_noti("Event: Start logging. Time: %s" % (time_now.strftime("%d, %b %Y; %-Hh:%-Mm:%-Ss")))

		print_warn("Last upgrade is not complete yet, rollback previous stable version")

		backupFolderRecoveryFlow = SiriusFirmwareRecovery.RecoveryFlowModel(SiriusFirmwareRecovery.BACKUP_FOLDER,
																			"BACKUP_FOLDER",
																			"BASELINE_FOLDER",
																			None)
		baselineFolderRecoveryFlow = SiriusFirmwareRecovery.RecoveryFlowModel(SiriusFirmwareRecovery.BASELINE_FOLDER,
																			"BASELINE_FOLDER",
																			"FACTORY_FOLDER",
																			None)
		factoryFolderRecoveryFlow = SiriusFirmwareRecovery.RecoveryFlowModel(SiriusFirmwareRecovery.FACTORY_FOLDER,
																			"FACTORY_FOLDER",
																			None,
																			None)

		SiriusRecoveryFlowPipeline = [
			backupFolderRecoveryFlow,
			baselineFolderRecoveryFlow,
			factoryFolderRecoveryFlow,
		]

		for flow in SiriusRecoveryFlowPipeline:
			print_noti("Try using \"%s\" to recovery firwmare to Sirius" % (flow["CUR_FOLDER_NAME"]))
			if SiriusFwValidator.ValidateFirmware(flow["FW_RECOVERY_MODELS"], flow["FW_IN_FOLDER"]) == True:

				# Do the recovery with current...
				retVal = SiriusFwRecoveryExecuter.RecoveryFirmware(flow["FW_RECOVERY_MODELS"], flow["CUR_FOLDER_NAME"])

				# if success, move current folder items to BASELINE FOLDER
				if retVal == 0:
					if SiriusFirmwareRecovery.BASELINE_FOLDER != flow["FW_IN_FOLDER"]:
						cmd = "rm -rf %s*" % SiriusFirmwareRecovery.BASELINE_FOLDER
						print_debug(cmd)
						os.system(cmd)
						cmd = "cp -rp %s* %s" % (flow["FW_IN_FOLDER"], SiriusFirmwareRecovery.BASELINE_FOLDER)
						print_debug(cmd)
						os.system(cmd)
					if SiriusFirmwareRecovery.BACKUP_FOLDER == flow["FW_IN_FOLDER"]:
						cmd = "rm -rf %s*" % SiriusFirmwareRecovery.BACKUP_FOLDER
						print_debug(cmd)
						os.system(cmd)
					return retVal

				# if no more folder, exit
				if flow["NEXT_FOLDER_NAME"] == None:
					return retVal

				# If fail, go to next folder...
				print_warn("Recovery operation of \"%s\" fail, use \"%s\" instead" % (flow["CUR_FOLDER_NAME"], flow["NEXT_FOLDER_NAME"]))
				continue
			else:
				print_warn("Validation of \"%s\" fail, use \"%s\" instead" % (flow["CUR_FOLDER_NAME"], flow["NEXT_FOLDER_NAME"]))

	except Exception as e:
		print_err(e.message)
		print(traceback.format_exc())
	finally:
		try:
			os.remove(SiriusFirmwareRecovery.FIRMWARE_UPGRADING_FLAG)
		except OSError:
			pass
		time_now = datetime.datetime.now()
		print_noti("Event: End logging. Time: %s" % (time_now.strftime("%d, %b %Y; %-Hh:%-Mm:%-Ss")))
		print_noti("<"*70)

		blink_led.StopThread()
		sys.exit(retVal)

if __name__ == "__main__":
	main()
