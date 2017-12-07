from pexpect import pxssh
import pexpect, getpass
import sys
import os
from pyexpect_common import *
from template_ifconfig_ip import *
from template_scp import *
from optparse import OptionParser, OptionGroup
import shutil
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

def CopyBaseline(targetFolder):
	SetNetworkInterface(HOST_INTERFACE, HOST_IP, HOST_PASSWORD)
	ScpDownloadFrom("/home/root/fw_backup/baseline", "root", BOARD_PASSWORD, BOARD_IP, targetFolder)

def ExtractAll(folder):
	for fn in os.listdir(folder):
		if fn.endswith(".tar.xz"):
			print ("=> Extracting: %s/%s" % (folder, fn))
			ret = os.system("bsdtar -xzf %s/%s -C %s" % (folder, fn, folder))
			if ret != 0:
				print ("Error when extracting %s/%s" % (folder, fn))

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

# xmsdk, svc, surisdk, suribl, eraser
# emvconf x 4 + capk
# pn5180
NUM_OF_FIRMWARE = 11

if __name__ == '__main__':
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
	(options, args) = parser.parse_args()

	if options.isCreateBaseline:
		CopyBaseline("./BASELINE")

	if options.fwPath != "":
		passCount = 0

		# download from sisius's current BASELINE to BASELINE_TARGET
		shutil.rmtree("./BASELINE_TARGET", ignore_errors=True)
		CopyBaseline("./BASELINE_TARGET")

		# copy from current BASELINE to BASELINE_TEMP
		shutil.rmtree("./BASELINE_TEMP", ignore_errors=True)
		shutil.copytree("./BASELINE", "./BASELINE_TEMP")

		# extract all compressed firmware in BASELINE_TEMP
		ExtractAll('./BASELINE_TEMP')
		# extract all compressed firmware in BASELINE_TARGET
		ExtractAll('./BASELINE_TARGET')

		# extract fwPath to BASELINE_TEMP
		print ("=> Extracting %s to BASELINE_TEMP" % (options.fwPath))
		os.system("bsdtar -xzvf %s -C ./BASELINE_TEMP" % (options.fwPath))

		# compare all json in BASELINE_TARGET with BASELINE_TEMP
		for fn in os.listdir('./BASELINE_TARGET'):
			path_target = "./BASELINE_TARGET/" + fn
			path_temp = "./BASELINE_TEMP/" + fn
			if fn.endswith(".json"):
				if os.path.isfile(path_temp):
					sys.stdout.write ("=> Comparing %-40.40s with   %-40.40s" % (path_target, path_temp))
					if DoHash(path_target) == DoHash(path_temp):
						print (" [OK]")
						passCount += 1
					else:
						print (" [FAIL]")
				else:
					print ("Missing %s" % (path_temp))

		if passCount >= NUM_OF_FIRMWARE:
			# if pass, ask for replace BASELINE_TEMP with current BASELINE
			if yes_or_no("Do you want to replace current firmware to BASELINE (for later comparison) ?") == True:
				shutil.rmtree("./BASELINE", ignore_errors=True)
				shutil.copytree("./BASELINE_TEMP", "./BASELINE")
		else:
			# if fail prompt error and exit
			print ("Compare firmware fail !!!")
