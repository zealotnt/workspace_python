import subprocess
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

def CopyBaseline(targetFolder):
	SetNetworkInterface(HOST_INTERFACE, HOST_IP, HOST_PASSWORD)
	ScpDownloadFrom("/home/root/fw_backup/baseline", "root", BOARD_PASSWORD, BOARD_IP, targetFolder)

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
		sys.stdout.write ("=> Extracting %s to BASELINE_TEMP" % (options.fwPath))
		extractedFile = Extractfile(options.fwPath, "./", "./BASELINE_TEMP")
		GotFirmware(extractedFile)

		# compare all json in BASELINE_TARGET with BASELINE_TEMP
		for fn in os.listdir('./BASELINE_TARGET'):
			path_target = "./BASELINE_TARGET/" + fn
			path_temp = "./BASELINE_TEMP/" + fn
			if fn.endswith(".json"):
				if os.path.isfile(path_temp):
					sys.stdout.write ("=> Comparing %-40.40s with   %-40.40s" % (path_target, path_temp))
					if DoHash(path_target) == DoHash(path_temp):
						print (" [%sOK%s]" % (bcolors.OKGREEN, bcolors.ENDC))
						passCount += 1
					else:
						print (" [%sFAIL%s]" % (bcolors.FAIL, bcolors.ENDC))
				else:
					print ("=> Missing %s" % (path_temp))

		if passCount >= NUM_OF_FIRMWARE:
			# if pass, ask for replace BASELINE_TEMP with current BASELINE
			if yes_or_no("Do you want to replace current firmware to BASELINE (for later comparison) ?") == True:
				shutil.rmtree("./BASELINE", ignore_errors=True)
				shutil.copytree("./BASELINE_TEMP", "./BASELINE")
		else:
			# if fail prompt error and exit
			print ("Compare firmware fail (pass %d/%d)!!!" % (passCount, NUM_OF_FIRMWARE))
