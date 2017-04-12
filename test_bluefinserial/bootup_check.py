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

FIRMWARE_BACKUP_FOLDER		= "/home/root/fw_backup/"
BACKUP_FACTORY_FOLDER 		= FIRMWARE_BACKUP_FOLDER + "factory/"
BACKUP_UPGRADES_FOLDER		= FIRMWARE_BACKUP_FOLDER + "upgrades/"

XMSDK_FW_FILE_NAME			= "xmsdk.json.tar.xz"
XMSDK_FACT_BAK_PATH 		= BACKUP_FACTORY_FOLDER + XMSDK_FW_FILE_NAME
XMSDK_UPG_BAK_PATH			= BACKUP_UPGRADES_FOLDER + XMSDK_FW_FILE_NAME

SVC_FW_FILE_NAME			= "svc.json.tar.xz"
SVC_FACT_BAK_PATH 			= BACKUP_FACTORY_FOLDER + SVC_FW_FILE_NAME
SVC_UPG_BAK_PATH			= BACKUP_UPGRADES_FOLDER + SVC_FW_FILE_NAME

SURIFW_FW_FILE_NAME			= "surisdk.json.tar.xz"
SURIFW_FACT_BAK_PATH 		= BACKUP_FACTORY_FOLDER + SURIFW_FW_FILE_NAME
SURIFW_UPG_BAK_PATH			= BACKUP_UPGRADES_FOLDER + SURIFW_FW_FILE_NAME

SURIBL_FW_FILE_NAME			= "suribootloader.json.tar.xz"
SURIBL_FACT_BAK_PATH 		= BACKUP_FACTORY_FOLDER + SURIBL_FW_FILE_NAME
SURIBL_UPG_BAK_PATH 		= BACKUP_UPGRADES_FOLDER + SURIBL_FW_FILE_NAME

SURI_ERASER_NAME			= "erasersigned.tar"
SURI_ERASER_PATH			= BACKUP_FACTORY_FOLDER + SURI_ERASER_NAME

FIRMWARE_UPGRADING_FLAG 	= FIRMWARE_BACKUP_FOLDER + "upg_flag"

SEND_SCP_SCRIPT 			= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/sendscp_mod.sh"
RF_SCP_EXTRACT_PATH 		= "/home/root/secureROM-Sirius/Host/customer_scripts/scripts/buildSCP/rf_fw/"
SEND_SCP_UART_PORT 			= "/dev/ttymxc3"

LOG_FILE_NAME				= "bootup_check.log"
LOG_FILE_PATH				= FIRMWARE_BACKUP_FOLDER + LOG_FILE_NAME
LOG_MODULE_NAME				= "bootup_check"
LOG_FILE_MAX_NUM			= 5
LOG_FILE_MAX_SIZE			= 10*1024 # 10KB

class FileLogging():
	def __init__(self, name, logFilePath):
		"""
		Creates a rotating log
		"""
		self.logger = logging.getLogger(name)
		self.logger.setLevel(logging.DEBUG)

		# add a rotating handler
		self.handler = RotatingFileHandler(logFilePath, maxBytes=LOG_FILE_MAX_SIZE, backupCount=LOG_FILE_MAX_NUM)
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
gLogger = FileLogging("bootup_check", LOG_FILE_PATH)

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
class ffirmware:
	UPDATED_FIRMWARE = [XMSDK_UPG_BAK_PATH, SVC_UPG_BAK_PATH, SURIFW_UPG_BAK_PATH, SURIBL_UPG_BAK_PATH]
	FACTORY_FIRMWARE = [XMSDK_FACT_BAK_PATH, SVC_FACT_BAK_PATH, SURIFW_FACT_BAK_PATH, SURIBL_FACT_BAK_PATH]
	FIRMWARE_JSON_PREFIX = ["xmsdk", "svc", "surisdk", "suribl"]
	IDX_XM = 0
	IDX_SVC = 1
	IDX_SURISDK = 2
	IDX_SURIBL = 3

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

SYSFS_GPIO_VALUE_HIGH = '1'
SYSFS_GPIO_VALUE_LOW = '0'

class BlinkLedThread(threading.Thread):
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
			self.f_red.write(SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_red.write(SYSFS_GPIO_VALUE_LOW)

		if (value & 0x02):
			self.f_green.write(SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_green.write(SYSFS_GPIO_VALUE_LOW)

		if (value & 0x04):
			self.f_blue.write(SYSFS_GPIO_VALUE_HIGH)
		else:
			self.f_blue.write(SYSFS_GPIO_VALUE_LOW)

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

def CheckFilePresence(file_path):
	if os.path.isfile(file_path) is not True:
		return FILE_ABSENT
	return FILE_PRESENT

def check_files_present(fileList):
	for file in fileList:
		# if absent, return right away
		if CheckFilePresence(file) == FILE_ABSENT:
			return FILE_ABSENT
	return FILE_PRESENT

def restore_app_firmware(file_restored, file_name, dry_run=False):
	"""
	:param file_restored: compress file to restore from
	:param file_name: the prefix of json in the firmware, and the output firmware
	:param dry_run: if true, the output file will be created. Otherwise, it won't

	:return: valid(bool), filename(string)
	"""

	# Try to restore
	if os.path.isfile(file_restored) is not True:
		print_warn("Firmware \"%s\" backup not found" % (file_restored))
		raise Exception("File %s not found" % (file_restored))

	# Extract tar file
	if dry_run == False:
		print_noti("Going to restore \"%s\" from \"%s\"" % (file_name, file_restored))
	extracted_file = Extractfile(file_restored)
	if extracted_file is None:
		raise Exception("Can\'t extract %s" % file_restored)

	# Decode json file
	return DecodeJsonAndWriteToFile(extracted_file, file_name, dry_run)

def check_bl_folder_valid(extract_result):
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
				return False
		else:
			# Not match, return right away
			return False
	return True, folder_name

def upgrade_suribl(compress_file):
	# Clean the old bootloader firmware folder
	os.system("rm -rf %s" % (RF_SCP_EXTRACT_PATH))
	os.system("mkdir -p %s" % (RF_SCP_EXTRACT_PATH))

	# detect the content of SCP bootloader firmware
	tarExamineCmd = "bsdtar -tf " + compress_file
	pListFile = subprocess.Popen(['bsdtar', '-tf', compress_file], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	output, err = pListFile.communicate()
	rc = pListFile.returncode
	ret, folder_name = check_bl_folder_valid(output)
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

def stop_svc_xmsdk():
	os.system("killall xmsdk")
	os.system("killall svc")

def run_svc(file_path):
	os.system("./" + file_path + " &")

def run_suri_upgrade(file_path):
	return os.system("./rfp_fwupgrade " + file_path)

def TestBlink():
	blink_led = BlinkLedThread("Led blinker")
	blink_led.start()
	try:
		while True:
			time.sleep(1)
	except:
		blink_led.StopThread()
		sys.exit(0)
	print_ok("Bootup check ok")

def ValidateUpgradeFirmwares():
	present = 0
	for idx, firmware in enumerate(ffirmware.UPDATED_FIRMWARE):
		try:
			# check validity of firmwares in folder
			ret, json = restore_app_firmware(firmware, ffirmware.FIRMWARE_JSON_PREFIX[idx], dry_run=True)
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

def RollbackFirmware(firmwareList, firmwareName):
	"""
	firmwareList should be the array with 4 element with the firmware order:
		1. XMSDK
		2. SVC
		3. SURIFW
		4. SURIBL
	"""
	print_noti("Going to rollback using \"%s firmwares\"" % (firmwareName))
	output_json_filename = ["", "", "", ""]

	if check_files_present(firmwareList) != FILE_PRESENT:
		print_err("Not all factory backup file present")
		return -1

	stop_svc_xmsdk()

	########################################################################
	# Step 1
	# Extract firmware from list of compressed files
	for idx, firmware in enumerate(firmwareList):
		ret, output_json_filename[idx] = restore_app_firmware(firmware, ffirmware.FIRMWARE_JSON_PREFIX[idx])
		if ret != True:
			print_err("Err when extract %s" % (ffirmware.FIRMWARE_JSON_PREFIX[idx]))
			return -1

	########################################################################
	# Step 2
	# Start roll back the firmware
	# first, try eraser the firmware in maxim
	# Note: If this step fail due to file not found, it is not a big deal, may be the flasher,...
	# Just continue with other firmwares
	print_noti("Going to erase Maxim firmware using \"%s\"" % (SURI_ERASER_PATH))
	ret = upgrade_suribl(SURI_ERASER_PATH)
	if ret != True:
		print_err("Err when erase maxim firwmare")
	print_ok("Erase Maxim firmware using \"%s\" successfully" % (SURI_ERASER_PATH))

	# suribl
	print_noti("Going to roll back suribl firmware using \"%s\"" % (ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURIBL]))
	ret = upgrade_suribl(ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURIBL])
	if ret != True:
		print_err("Err when roll back suribl")
		return -1
	print_ok("Roll back firmware \"%s\" ok" % (ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURIBL]))

	# svc
	print_noti("Start svc service \"%s\"" % (ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SVC]))
	run_svc(ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SVC])

	# surisdk
	print_noti("Going to roll back surisdk firmware using \"%s\"" % (ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURISDK]))
	ret = run_suri_upgrade(ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURISDK])
	if ret != 0:
		print_err("Err when roll back surisdk")
		return -1
	print_ok("Roll back firmware \"%s\" ok" % (ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURISDK]))

	# xmsdk will be start later, after exit this script, done by startup.sh

	########################################################################
	# Step 3
	# Clean up everything
	os.remove(FIRMWARE_UPGRADING_FLAG)
	os.remove(ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURISDK])
	os.remove(ffirmware.FIRMWARE_JSON_PREFIX[ffirmware.IDX_SURIBL])

	for json_file in output_json_filename:
		# os.remove(xm_json)
		# os.remove(svc_json)
		# os.remove(surifw_json)
		# os.remove(suribl_json)
		os.remove(json_file)

	stop_svc_xmsdk()
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
	if os.path.isfile(FIRMWARE_UPGRADING_FLAG) == False:
		print_ok("Bootup check ok", False)
		return

	# If firmware_upgrading_flag file is present, rollback for all
	blink_led = BlinkLedThread("Led blinker")
	blink_led.start()
	retVal = -1
	try:
		print_noti(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
		time_now = datetime.datetime.now()
		print_noti("Event: Start logging. Time: %s" % (time_now.strftime("%d, %b %Y; %-Hh:%-Mm:%-Ss")))

		print_warn("Last upgrade is not complete yet, rollback previous stable version")
		#########################################################################################
		# Step 1
		# check validity of firmwares in upgrade folder
		if ValidateUpgradeFirmwares() != True:
			print_warn("Validation of \"upgrades firmware\" fail, use \"factory firmware\" instead")
			# if at least one firmware json is invalid
			# choose firmware in factory folder to roll back
			retVal = RollbackFirmware(ffirmware.FACTORY_FIRMWARE, "factory")
			return

		#########################################################################################
		# Step 2
		# check if there is enough 4 type of firmware in the BACKUP_UPGRADES_FOLDER folder
		# if it missing some file, collect the file from BACKUP_FACTORY_FOLDER
		firmwareUpgrades = ["", "", "", ""]
		# get available firmware from upgrade folder
		for idx, firmware in enumerate(ffirmware.UPDATED_FIRMWARE):
			if CheckFilePresence(firmware) == FILE_PRESENT:
				firmwareUpgrades[idx] = firmware
				print_noti("Got \"upgrade firmware\" \"%s\"" % (firmware))
		# if any firmware type is missing, get them from factory folder
		for idx, firmware in enumerate(firmwareUpgrades):
			if firmware == "":
				print_noti("Using \"factory firmware\" \"%s\" instead" % (ffirmware.FACTORY_FIRMWARE[idx]))
				firmwareUpgrades[idx] = ffirmware.FACTORY_FIRMWARE[idx]
		# rollback from the collected firmware
		ret = RollbackFirmware(firmwareUpgrades, "upgrades")

		#########################################################################################
		# Step 3
		# if the roll back is fail
		# try rolling back to factory firmware
		if ret != 0:
			retVal = RollbackFirmware(ffirmware.FACTORY_FIRMWARE, "factory - last try")
		# else, it is ok now, roll back process is ok, return to reader application
		else:
			retVal = 0
		return
	except Exception as e:
		print_err(e.message)
	finally:
		time_now = datetime.datetime.now()
		print_noti("Event: End logging. Time: %s" % (time_now.strftime("%d, %b %Y; %-Hh:%-Mm:%-Ss")))
		print_noti("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

		blink_led.StopThread()
		sys.exit(retVal)

if __name__ == "__main__":
	main()