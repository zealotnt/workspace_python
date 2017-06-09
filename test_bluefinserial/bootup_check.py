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
from logging.handlers import RotatingFileHandler

# ---- CONSTANTS
FILE_PRESENT 				= 0
FILE_ABSENT 				= 1

SEND_SCP_SCRIPT 			= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/sendscp_mod.sh"
RF_SCP_EXTRACT_PATH 		= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/buildSCP/rf_fw/"
SEND_SCP_UART_PORT 			= "/dev/ttymxc3"

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

	SURI_ERASER_NAME			= "erasersigned.tar"
	SURI_ERASER_PATH			= FACTORY_FOLDER + SURI_ERASER_NAME
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
	def FirmwareAccess():
		return [
			"ERASER",
			"SURIBL",
			"SURISDK",
			"PN5180",
			"EMV_CONF0",
			"EMV_CONF1",
			"EMV_CONF2",
			"EMV_CONF3",
			"EMV_CAPK",
			"SVC",
			"XMSDK"
		]

	@staticmethod
	def FirmwareUpgradeFunction():
		return {
			"ERASER": SiriusFwRecoveryExecuter.UpgradeSuribl,
			"SURIBL": SiriusFwRecoveryExecuter.UpgradeSuribl,
			"SURISDK": SiriusFwRecoveryExecuter.UpgradeSurisdk,
			"PN5180": SiriusFwRecoveryExecuter.UpgradePn5180,
			"EMV_CONF0": SiriusFwRecoveryExecuter.UpgradeEmv,
			"EMV_CONF1": SiriusFwRecoveryExecuter.UpgradeEmv,
			"EMV_CONF2": SiriusFwRecoveryExecuter.UpgradeEmv,
			"EMV_CONF3": SiriusFwRecoveryExecuter.UpgradeEmv,
			"EMV_CAPK": SiriusFwRecoveryExecuter.UpgradeEmv,
			"SVC": None,
			"XMSDK": None,
		}

	@staticmethod
	def FirmwareRecoverList(inFolder):
		"""
		inFolder: path (best if absolute path) to folder contains all of the folder

		ret: return the dictionary of recovery firmwares, all of them are contain in `inFolder`
		"""
		return {
			"ERASER": SiriusFirmwareRecovery.SURI_ERASER_PATH,
			"SURIBL": inFolder + SiriusFirmwareRecovery.SURIBL_FW_FILE_NAME,
			"SURISDK": inFolder + SiriusFirmwareRecovery.SURISDK_FW_FILE_NAME,
			"PN5180": inFolder + SiriusFirmwareRecovery.PN5180_FW_FILE_NAME,
			"EMV_CONF0": inFolder + SiriusFirmwareRecovery.EMV_CONF0_FILE_NAME,
			"EMV_CONF1": inFolder + SiriusFirmwareRecovery.EMV_CONF1_FILE_NAME,
			"EMV_CONF2": inFolder + SiriusFirmwareRecovery.EMV_CONF2_FILE_NAME,
			"EMV_CONF3": inFolder + SiriusFirmwareRecovery.EMV_CONF3_FILE_NAME,
			"EMV_CAPK": inFolder + SiriusFirmwareRecovery.EMV_CAPK_FILE_NAME,
			"SVC": inFolder + SiriusFirmwareRecovery.SVC_FW_FILE_NAME,
			"XMSDK": inFolder + SiriusFirmwareRecovery.XMSDK_FW_FILE_NAME,
		}

	@staticmethod
	def FirmwareJsonPrefix():
		return {
			"ERASER": "suribl",
			"SURIBL": "suribl",
			"SURISDK": "surisdk",
			"PN5180": "pn5180",
			"EMV_CONF0": "",
			"EMV_CONF1": "",
			"EMV_CONF2": "",
			"EMV_CONF3": "",
			"EMV_CAPK": "",
			"SVC": "svc",
			"XMSDK": "xmsdk"
		}

	@staticmethod
	def UpgradeActionName():
		return {
			"ERASER": "Erase RF Processor flash memory",
			"SURIBL": "Recovery suri bootloader",
			"SURISDK": "Recovery surisdk",
			"PN5180": "Recovery pn5180 firmware",
			"EMV_CONF0": "Recovery emvConf0",
			"EMV_CONF1": "Recovery emvConf1",
			"EMV_CONF2": "Recovery emvConf2",
			"EMV_CONF3": "Recovery emvConf3",
			"EMV_CAPK": "Recovery emvCapk",
			"SVC": "",
			"XMSDK": ""
		}

	@staticmethod
	def FirmwareRecoveryModel(upgFunc, fwFile, jsonPrefix, actionName):
		return {
			"UPG_FUNC": upgFunc,
			"FIRMWARE_FILE": fwFile,
			"JSON_PREFIX": jsonPrefix,
			"ACTION_NAME": actionName,
		}

	@staticmethod
	def RecoveryFlowModel(fwInFolder, nextFolderName, curFolderName, tearDownFunc=None):
		fwAccess = SiriusFirmwareRecovery.FirmwareAccess()
		listFw = SiriusFirmwareRecovery.FirmwareRecoverList(fwInFolder)
		upgFunc = SiriusFirmwareRecovery.FirmwareUpgradeFunction()
		jsonNames = SiriusFirmwareRecovery.FirmwareJsonPrefix()
		actionNames = SiriusFirmwareRecovery.UpgradeActionName()
		fwRecoveryModels = []
		for idx, accessName in enumerate(fwAccess):
			fwRecoveryModels.append(
				SiriusFirmwareRecovery.FirmwareRecoveryModel(upgFunc[accessName],
									  listFw[accessName],
									  jsonNames[accessName],
									  actionNames[accessName])
			)

		return {
			"FW_RECOVERY_MODELS": fwRecoveryModels,
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
		self.handler = RotatingFileHandler(logFilePath, maxBytes, backupCount)
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

		tarCmd = "bsdtar -xvf " + file_path
		rc = os.system(tarCmd)
		if rc != 0:
			print_err("err when extracting file " + file_path)
			return None
		return output

	@staticmethod
	def DecodeJsonAndWriteToFile(json_file, target_name, dry_run=False):
		json_file_name = json_file.replace("\r", "").replace("\n", "")

		try:
			json_text = open(json_file[:len(json_file)-1], 'rb').read()
			json_decoded = json.loads(json_text)
		except Exception as e:
			raise Exception("Json decode file \"%s\" error: %s" % (json_file_name, str(e.message)))

		fw_dict = {key: value for (key, value) in (json_decoded.items())}
		if dry_run == False:
			print_debug(target_name + "'s md5 =" + fw_dict[target_name + "_md5"])
			print_debug(target_name + "'s metadata =" + fw_dict[target_name + "_metadata"])
		json_md5 = fw_dict[target_name + "_md5"]
		json_based64 = fw_dict[target_name + "_fw"]
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
			print_err('Json: %s\'s md5 is not equal to calculated value' % json_file)
			raise Exception('Json: %s\'s md5 is not equal to calculated value' % json_file)

		# if it is only for validating, no need to write to file
		if dry_run == True:
			return True, json_file[:len(json_file) - 1]

		# Everything is ok, write to target_name file
		try:
			fh = open(target_name, 'wb')
			fh.write(json_binary)
			fh.close()

			os.chmod(target_name, 0777)
		except Exception as e:
			raise Exception("Write result file \"%s\" from \"%s\" err: %s" % (target_name, json_file_name, str(e.message)))

		print_ok("Restore binary file \"%s\" ok" % (target_name))
		return True, json_file[:len(json_file) - 1]

	@staticmethod
	def CheckFilePresence(file_path):
		if os.path.isfile(file_path) is not True:
			return FILE_ABSENT
		return FILE_PRESENT

	@staticmethod
	def RestoreJsonFromCompressed(file_compressed, json_prefix, dry_run=False):
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
		if dry_run == False:
			print_noti("Going to restore \"%s\" from \"%s\"" % (json_prefix, file_compressed))
		extracted_file = SiriusFwValidator.Extractfile(file_compressed)
		if extracted_file is None:
			raise Exception("Can\'t extract %s" % file_compressed)

		# Decode json file
		return SiriusFwValidator.DecodeJsonAndWriteToFile(extracted_file, json_prefix, dry_run)

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
	def ValidateFirmware(fwRecoveryModel):
		present = 0
		for idx, model in enumerate(fwRecoveryModel):
			try:
				# check validity of model in folder
				ret, json = SiriusFwValidator.RestoreJsonFromCompressed(model["FIRMWARE_FILE"], model["JSON_PREFIX"], dry_run=True)
				if ret != True:
					print_err("Err when extract file")
				present += 1
			except Exception as e:
				err_msg = e.message
				if "not found" in err_msg:
					continue
				else:
					print_err(str(err_msg))
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
	def UpgradeSuribl(compress_file):
		# Clean the old bootloader firmware folder
		os.system("rm -rf %s" % (RF_SCP_EXTRACT_PATH))
		os.system("mkdir -p %s" % (RF_SCP_EXTRACT_PATH))

		# detect the content of SCP bootloader firmware
		tarExamineCmd = "bsdtar -tf " + compress_file
		pListFile = subprocess.Popen(['bsdtar', '-tf', compress_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = pListFile.communicate()
		rc = pListFile.returncode
		ret, folder_name = SiriusFwValidator.IsSCPFolderValid(output)
		if ret != True:
			print_err("Content in suribl is not valid !!!")
			return False

		# now, extract the firmware
		tarCmd = "bsdtar -xvf " + compress_file + " -C " + RF_SCP_EXTRACT_PATH
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
	def RunSvc(file_path):
		os.system("./" + file_path + " &")

	@staticmethod
	def UpgradeSurisdk(file_path):
		return os.system("./rfp_fwupgrade " + file_path)

	@staticmethod
	def UpgradePn5180(file_path):
		return os.system("./rfp_fwupgrade " + file_path)

	@staticmethod
	def UpgradeEmv(file_path):
		"""
		This function is used to upgrade emvconf0-3 or emvcapk
		"""
		return os.system("./rfp_fwupgrade " + file_path)

	@staticmethod
	def RecoveryFirmware(fwRecoveryModel, firmwareName):
		"""
		fwRecoveryModel should be the array which contains a type:

		"""
		print_noti("Going to rollback using \"%s firmwares\"" % (firmwareName))
		output_json_filename = []

		for idx, model in enumerate(fwRecoveryModel):
			if SiriusFwValidator.CheckFilePresence(model["FIRMWARE_FILE"]) != FILE_PRESENT:
				print_err("Not all %s files present" % firmwareName)
				return -1

		SiriusFwRecoveryExecuter.KillSvcXmsdk()

		########################################################################
		# Step 1
		# Extract firmware from list of compressed files
		for idx, model in enumerate(fwRecoveryModel):
			ret, output_json_filename[idx] = SiriusFwValidator.RestoreJsonFromCompressed(
				model["FIRMWARE_FILE"],
				model["JSON_PREFIX"]
			)
			if ret != True:
				print_err("Err when extract %s" % model["FIRMWARE_FILE"])
				return -1

		########################################################################
		# Step 2
		# Start roll back the firmware one by one
		for idx, model in enumerate(fwRecoveryModel):
			print_noti("Going to %s using \"%s\"" % (model["ACTION_NAME"], model["FIRMWARE_FILE"]))
			model["UPG_FUNC"](output_json_filename[idx])
			if ret != True:
				print_err("Err when %s" % model["ACTION_NAME"])
				return -1
			print_ok("%s using \"%s\" successfully" % (model["ACTION_NAME"], model["FIRMWARE_FILE"]))

		########################################################################
		# Step 3
		# Clean up everything
		for json_file in output_json_filename:
			os.remove(json_file)

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
																			"BASELINE_FOLDER",
																			"BACKUP_FOLDER",
																			None)
		baselineFolderRecoveryFlow = SiriusFirmwareRecovery.RecoveryFlowModel(SiriusFirmwareRecovery.BASELINE_FOLDER,
																			"FACTORY_FOLDER",
																			"BASELINE_FOLDER",
																			None)
		factoryFolderRecoveryFlow = SiriusFirmwareRecovery.RecoveryFlowModel(SiriusFirmwareRecovery.FACTORY_FOLDER,
																			None,
																			"FACTORY_FOLDER",
																			None)

		SiriusRecoveryFlowPipeline = [
			backupFolderRecoveryFlow,
			baselineFolderRecoveryFlow,
			factoryFolderRecoveryFlow,
		]

		for flow in SiriusRecoveryFlowPipeline:
			if SiriusFwValidator.ValidateFirmware(flow["FW_RECOVERY_MODELS"]) == True:
				# Do the recovery with current...
				retVal = SiriusFwRecoveryExecuter.RecoveryFirmware(flow["FW_RECOVERY_MODELS"], "")

				# If there is  teardown function, call it

			# If fail, go to next folder...
			else:
				print_warn("Validation of \"%s\" fail, use \"%s\" instead" % (flow["CUR_FOLDER_NAME"], flow["NEXT_FOLDER_NAME"]))

	except Exception as e:
		print_err(e.message)
	finally:
		os.remove(SiriusFirmwareRecovery.FIRMWARE_UPGRADING_FLAG)
		time_now = datetime.datetime.now()
		print_noti("Event: End logging. Time: %s" % (time_now.strftime("%d, %b %Y; %-Hh:%-Mm:%-Ss")))
		print_noti("<"*70)

		blink_led.StopThread()
		sys.exit(retVal)

if __name__ == "__main__":
	main()
