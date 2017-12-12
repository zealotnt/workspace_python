#!/usr/bin/env python

import subprocess
from pexpect import pxssh
import pexpect, getpass
import sys
import os
import json
from pyexpect_common import *
from template_ifconfig_ip import *
from template_scp import *
from optparse import OptionParser, OptionGroup
import shutil
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

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

def print_err(text):
	print >> sys.stderr, bcolors.FAIL + text + bcolors.ENDC

def print_noti(text, isBold=False):
	extra1 = ""
	if isBold == True:
		extra1 = bcolors.BOLD
	print (extra1 + bcolors.WARNING + text + bcolors.ENDC)

def CopyBaseline(targetFolder):
	SetNetworkInterface(HOST_INTERFACE, HOST_IP, HOST_PASSWORD)
	ScpDownloadFrom("/home/root/fw_backup/baseline", "root", TARGET_PASSWORD, TARGET_IP, targetFolder)

def GotFirmware(obj):
	print (" ... Got %s%s%s" % (bcolors.OKGREEN, obj, bcolors.ENDC))

def Extractfile(file_path, from_folder, to_folder):
	tarExamineCmd = "bsdtar -tf %s/%s" % (from_folder, file_path)
	pListFile = subprocess.Popen(['bsdtar', '-tf', from_folder+"/"+file_path],
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)
	output, err = pListFile.communicate()
	rc = pListFile.returncode

	tarCmd = "bsdtar -xzf %s/%s -C %s" % (from_folder, file_path, to_folder)
	rc = os.system(tarCmd)
	if rc != 0:
		print_err("err when extracting file " + file_path)
		return None
	if output.count("\n") <= 1:
		# only 1 firmware, strip the new line
		output = output.strip('\n')
		output = output.strip('\r')
		pass
	else:
		# multiple firmware in a compressed file
		output = output.replace("\r\n", ",")
		output = output.replace("\n\r", ",")
		output = output.replace("\r", ",")
		output = output.replace("\n", ",")
	return output

def ExtractAll(folder):
	for fn in os.listdir(folder):
		if fn.endswith(".tar.xz"):
			sys.stdout.write ("=> Extracting: %s/%-30.30s to %s" % (folder, fn, folder))
			extractedFile = Extractfile(fn, folder, folder)
			GotFirmware(extractedFile)
			if os.path.basename(extractedFile) != extractedFile:
				path_from = folder+"/"+extractedFile
				path_to = folder+"/"+os.path.basename(extractedFile)
				print ("\t move %s to %s" % (path_from, path_to))
				shutil.move(path_from, path_to)

def DoHash(file_path):
	with open(file_path, "rb") as f:
		binary_data = f.read()
		hashEngine = hashes.Hash(hashes.SHA1(), backend=default_backend())
		hashEngine.update(binary_data)
		return hashEngine.finalize()

def yes_or_no(question):
	reply = str(raw_input(question+' (y/n): ')).lower().strip()
	if reply[0] == 'y':
		return True
	if reply[0] == 'n':
		return False
	else:
		return yes_or_no("Uhhhh... please enter ")

def CompareDict(dict1, dict2):
	isPassed = True
	missing_keys_1 = [k for k in dict1 if k not in dict2]
	missing_keys_2 = [k for k in dict2 if k not in dict1]
	diff_keys = [k for k in dict1 if k in dict2 and dict1[k] != dict2[k]]
	if (len(diff_keys) != 0 or
		len(missing_keys_1) != 0 or
		len(missing_keys_2) != 0):
			print("\r\n\tSomething wrong:")
			isPassed = False
	for k in diff_keys:
		print "\t\tDiff: " + k
	for k in missing_keys_2:
		print "\t\tDict1 missing: " + k
	for k in missing_keys_1:
		print "\t\tDict2 missing: " + k
	return isPassed

def GetNumberFromUser(prompt):
	user_prompt = input(prompt)
	return int(user_prompt)

def GetPn5180Info(pn5180Obj):
	info = "pn5180_conn-"
	info += "local" if pn5180Obj["pn5180_connection"] == 0 else "remote"
	info += "_id-%d" % pn5180Obj["pn5180_id"]
	info += "_force" if pn5180Obj["pn5180_forceID"] == 1 else ""
	info += "_v" + pn5180Obj["pn5180_fwVer"]
	if "pn5180_rfconf" in pn5180Obj and pn5180Obj["pn5180_rfconf"] != "":
		info += "_cfg"
	return info

def TrickyFirmwareConverter(objs):
	# This function use to convert file name that SFIT produces
	# to match with the file name that xmsdk produces
	# so they can be compared with each other later on
	if objs == "1.json":
		path_from = "./BASELINE_TEMP/" + objs
		path_to = "./BASELINE_TEMP/" + "pn5180.json"
		print ("\t rename from %s to %s" % (path_from, path_to))
		shutil.move(path_from, path_to)

def TrickyFirmwareComparer(file_name, path_target, path_temp):
	if file_name == "pn5180.json":
		isPassed = False
		pn5180_target = json.loads(open(path_target).read())
		pn5180_temp = json.loads(open(path_temp).read())

		# get the item user wants to compare in pn5180_target:
		if len(pn5180_target) != 1:
			print ("\r\n\tPN5180_TARGET has %d firmware: " % (len(pn5180_target)))
			fw_count = 0
			for fw in pn5180_target:
				print "\t%d. %s" % (fw_count, GetPn5180Info(fw))
				fw_count += 1

			idx = GetNumberFromUser("\tPlease choose one:")
			pn5180_target = pn5180_target[idx]
		else:
			pn5180_target = pn5180_target[0]

		# get the item user wants to compare in pn5180_temp:
		if len(pn5180_temp) != 1:
			print ("\r\n\tPN5180_TEMP has %d sub-firmware: " % (len(pn5180_temp)))
			fw_count = 0
			for fw in pn5180_temp:
				print "\t% d. %s" % (fw_count, GetPn5180Info(fw))
				fw_count += 1

			idx = GetNumberFromUser("\tPlease choose one:")
			pn5180_temp = pn5180_temp[idx]
		else:
			pn5180_temp = pn5180_temp[0]

		# Note:
		# the force id in SIRIUS when upgraded ok always set to 1
		pn5180_temp["pn5180_forceID"] = 1

		# compare two firmware
		if CompareDict(pn5180_target, pn5180_temp):
			isPassed = True
		return isPassed

	# Default: Fail
	return False

# xmsdk, svc, surisdk, suribl, eraser
# emvconf x 4 + capk
# pn5180
NUM_OF_FIRMWARE = 11

def main():
	parser = OptionParser()
	parser.add_option(  "-c", "--create-baseline",
						dest="isCreateBaseline",
						action="store_true",
						default=False,
						help="to create the baseline of current folder from Sirius")
	parser.add_option(  "-p", "--path",
						dest="fwPath",
						default="",
						help="path to firmware to added to baseline")
	parser.add_option(  "-v", "--validate-only",
						dest="isValidateOnly",
						action="store_true",
						default=False,
						help="Only do the validate baseline of Sirius of Host's current BASELINE")
	(options, args) = parser.parse_args()

	if options.isCreateBaseline:
		print_noti("0. Creating BASELINE", isBold=True)
		shutil.rmtree("./BASELINE", ignore_errors=True)
		CopyBaseline("./BASELINE")

	if options.fwPath != "" or options.isValidateOnly == True:
		if options.fwPath != "" and not os.path.isfile(options.fwPath):
			print_err("Can't find %s" % options.fwPath)
			sys.exit(-1)

		passCount = 0

		# download from sisius's current BASELINE to BASELINE_TARGET
		print_noti("1. Download SIRIUS's BASELINE, save it to BASELINE_TARGET", isBold=True)
		shutil.rmtree("./BASELINE_TARGET", ignore_errors=True)
		CopyBaseline("./BASELINE_TARGET")

		# copy from current BASELINE to BASELINE_TEMP
		print_noti("2. Copy our saved BASELINE, to BASELINE_TEMP", isBold=True)
		shutil.rmtree("./BASELINE_TEMP", ignore_errors=True)
		shutil.copytree("./BASELINE", "./BASELINE_TEMP")

		# extract all compressed firmware in BASELINE_TEMP
		print_noti("3. Prepare all firmware to compare", isBold=True)
		print_noti("3.1 Extract all in BASELINE_TEMP")
		ExtractAll('./BASELINE_TEMP')
		# extract all compressed firmware in BASELINE_TARGET
		print_noti("3.2 Extract all in BASELINE_TARGET")
		ExtractAll('./BASELINE_TARGET')

		# extract fwPath to BASELINE_TEMP
		if options.fwPath != "" and options.isValidateOnly == False:
			print_noti("3.3 Extract firmware in newly upgraded firmware to BASELINE_TEMP")
			sys.stdout.write ("=> Extracting %s to BASELINE_TEMP" % (options.fwPath))
			extractedFile = Extractfile(options.fwPath, "./", "./BASELINE_TEMP")
			GotFirmware(extractedFile)
			TrickyFirmwareConverter(extractedFile)
		else:
			print_noti("3.3 Won't extract newly upgraded firmware, validate only")

		# compare all json in BASELINE_TARGET with BASELINE_TEMP
		print_noti("4. Do the firmware validation", isBold=True)
		for fn in os.listdir('./BASELINE_TARGET'):
			path_target = "./BASELINE_TARGET/" + fn
			path_temp = "./BASELINE_TEMP/" + fn
			if fn.endswith(".json"):
				if os.path.isfile(path_temp):
					sys.stdout.write ("=> Comparing %-40.40s with   %-40.40s" % (path_target, path_temp))
					if DoHash(path_target) == DoHash(path_temp):
						print (" [%sOK-Hash%s]" % (bcolors.OKGREEN, bcolors.ENDC))
						passCount += 1
					else:
						if TrickyFirmwareComparer(fn, path_target, path_temp):
							print (" [%sOK-Compare%s]" % (bcolors.OKGREEN, bcolors.ENDC))
							passCount += 1
						else:
							print (" [%sFAIL%s]" % (bcolors.FAIL, bcolors.ENDC))
				else:
					print ("=> Missing %s" % (path_temp))

		if passCount >= NUM_OF_FIRMWARE:
			print_noti("Validation result: ALL PASSED")
			# if pass, ask for replace BASELINE_TARGET to current BASELINE
			# ** BASELINE -> should be copied from BASELINE_TARGET
			# (because if we make BASELINE from BASELINE_TEMP,
			# the pn5180 firmware isnt' really updated,
			# remmembered, we extract new-pn5180-fw to BASELINE_TEMP,
			# then choose which firmware to compare with BASELINE_TARGET)
			prompt = "Do you want to replace current firmware BASELINE_TARGET to BASELINE (for later comparison) ?"
			if options.isValidateOnly == False and yes_or_no(prompt) == True:
				shutil.rmtree("./BASELINE", ignore_errors=True)
				shutil.copytree("./BASELINE_TARGET", "./BASELINE")
		else:
			# if fail prompt error and exit
			print_err ("Compare firmware fail (pass %d/%d)!!!" % (passCount, NUM_OF_FIRMWARE))

if __name__ == '__main__':
	main()
