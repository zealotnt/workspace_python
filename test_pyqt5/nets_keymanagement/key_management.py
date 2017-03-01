#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# System packages
import sys
import json
import os
import inspect
import zipfile
import glob

# Qt packages
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
	QAction, QTabWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout,
	QFileDialog, QMessageBox, QInputDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

# Cryptography packages
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric import utils

# Autogenerated package
import mainwindow_gui_auto

#######################################################################
# Constant declaration
#######################################################################
APP_VERSION_MAJOR		= 0
APP_VERSION_MINOR		= 0
APP_VERSION_REV			= 1

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
WINDOWS_TITLE = "STYL Key Management"

CASIGN_EXE				= os.path.join(CURRENT_DIR, "Casign", "ca_sign_build.exe")
SESSION_BUILD_EXE		= os.path.join(CURRENT_DIR, "session_build", "session_build.exe")
RAW_KEY_FILE			= CURRENT_DIR + "firmware_sign_key.raw"
CASIGN_INI_FILE			= CURRENT_DIR + "ca_sign_build.ini"
SESSION_BUILD_INI_FILE 	= CURRENT_DIR + "session_build.ini"
SB_SCRIPT_FILE 			= CURRENT_DIR + "sb_script.txt"
FIRMWARE_BL_SIGNED		= CURRENT_DIR + "suribl.signed.bin"
FIRMWARE_SDK_SIGNED_NAME= "surisdk.signed.bin"
BINARY_S19_FILE_NAME	= "binary.s19"
BINARY_S19_FILE 		= CURRENT_DIR + BINARY_S19_FILE_NAME
SB_SCRIPT_CONTENT 		= "write-file %s" % (BINARY_S19_FILE_NAME)
SCP_OUT_DIR_NAME		= "scp_out"
SCP_OUT_DIR				= CURRENT_DIR + SCP_OUT_DIR_NAME
BL_ZIP_OUT_NAME			= "bootloader.zip"
SRK_KEY_NAME			= "maximtestcrk.key"

def bigIntToBytes(big_val):
	# [Ref](http://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3)
	bit_length = (big_val.bit_length() + 7) // 8
	return big_val.to_bytes(bit_length, 'big')

def checkPriKeyEncrypted(prikeyPath):
	with open(prikeyPath, "r") as f:
		serialized_private = f.read()
		serialized_private_bytes = str.encode(serialized_private)
		f.close()

	try:
		loaded_pri_key = serialization.load_pem_private_key(
				serialized_private_bytes,
				password=None,
				backend=default_backend()
			)
	except Exception as inst:
		if ("is encrypted" in str(inst)):
			return True

	return False

def genRawMaximKey(pemPriKeyPath, keyPass, outFileName):
	with open(pemPriKeyPath, "r") as f:
		serialized_private = f.read()
		serialized_private_bytes = str.encode(serialized_private)
		f.close()

	if keyPass is not None:
		keyPass = str.encode(keyPass)

	loaded_pri_key = serialization.load_pem_private_key(
			serialized_private_bytes,
			password=keyPass,
			backend=default_backend()
		)

	public_key = loaded_pri_key.public_key()

	# dump_hex(public_key.public_numbers().x, 'Pub X bytes: ', token=', ', prefix='0x', wrap=8)
	# dump_hex(public_key.public_numbers().y, 'Pub Y bytes: ', token=', ', prefix='0x', wrap=8)
	# dump_hex(loaded_pri_key.private_numbers().private_value, 'Pri bytes: ', token=', ', prefix='0x', wrap=8)

	pri_bytes = bigIntToBytes(loaded_pri_key.private_numbers().private_value)
	x_pub_bytes = bigIntToBytes(public_key.public_numbers().x)
	y_pub_bytes = bigIntToBytes(public_key.public_numbers().y)

	with open(outFileName, "w") as f:
		for c in pri_bytes:
			f.write("%02x" % (c))
		f.write("\n")

		for c in x_pub_bytes:
			f.write("%02x" % (c))
		f.write("\n")

		for c in y_pub_bytes:
			f.write("%02x" % (c))
		f.write("\n")

		f.close()

		return True

def zipDir(folderPath, outputZip):
	zipf = zipfile.ZipFile(outputZip, 'w', zipfile.ZIP_DEFLATED)
	for root, dirs, files in os.walk(folderPath):
		for file in files:
			zipf.write(os.path.join(root, file))
	zipf.close()
	return True

def genS19File(binPath):
	command = 'objcopy -I binary -O srec --srec-forceS3 --srec-len=128 --adjust-vma 0x10000000 %s %s' % (binPath, BINARY_S19_FILE)
	os.system(command)

def genPacketDotList(scpOutPath):
	list_files = glob.glob(scpOutPath + os.sep + '*.packet')
	list_files = sorted(list_files)
	with open(scpOutPath + os.sep + 'packet.list', "w") as f:
		for file in list_files:
			f.write("%s\n" % file)
		f.close()

def signFirmware(keyPath, keyPass, firmwarePath, outputZipDir, firmwareType):
	casign_ini_file = {
		"algo": "ecdsa",
		"ecdsa_file": SRK_KEY_NAME,
		"ca": "suribootloader.bin",
		"sca": FIRMWARE_BL_SIGNED,
		"load_address": "10000000",
		"jump_address": "10000020",
		"arguments": "",
		"application_version": "010A0B03",
		"version": "01000003",
		"verbose": "yes"
	}
	session_ini_file = {
		"session_mode": "SCP_ANGELA_ECDSA",
		"verbose": "no",
		"output_file": "%s%sscp" % (SCP_OUT_DIR, os.sep),
		"pp": "ECDSA",
		"addr_offset": "00000000",
		"chunk_size": "4094",
		"script_file": "sb_script.txt",
		"ecdsa_file": SRK_KEY_NAME
	}

	# Check the validity of private key and Generate the raw value of private key
	genRawMaximKey(keyPath, keyPass, SRK_KEY_NAME)

	# Write the "ca_sign_build.ini" file
	casign_ini_file['ca'] = firmwarePath
	outPutFIle = ""
	if firmwareType == "SURIBL":
		casign_ini_file['header'] = 'yes'
		casign_ini_file['sca'] = FIRMWARE_BL_SIGNED
		outPutFIle = outputZipDir + os.sep + BL_ZIP_OUT_NAME
	else:
		outPutFIle = outputZipDir + os.sep + FIRMWARE_SDK_SIGNED_NAME
		casign_ini_file['sca'] = outPutFIle

	with open(CASIGN_INI_FILE, "w", newline='') as f:
		for item in casign_ini_file:
			print(item, casign_ini_file[item])
			f.write("%s=%s\n" % (item, casign_ini_file[item]))
		f.close()

	# Sign the firmware with Casign
	if firmwareType == "SURIBL":
		# Sign with full param
		os.system(CASIGN_EXE)
		pass
	elif firmwareType == "SURISDK":
		# Sign without the 32bytes header
		os.system(CASIGN_EXE)
		return (firmwarePath, outPutFIle)
	else:
		msgBoxError("Error", "Unregcognize firmware type: %s" % firmwareType)
		return None

	# Generate the SCP packets if the firmware is bootloader
	if firmwareType == "SURIBL":
		with open(SB_SCRIPT_FILE, "w", newline='') as f:
			f.write("%s\n" % SB_SCRIPT_CONTENT)
			f.close()

		with open(SESSION_BUILD_INI_FILE, "w", newline='') as f:
			for item in session_ini_file:
				print(item, session_ini_file[item])
				f.write("%s=%s\n" % (item, session_ini_file[item]))
			f.close()

		genS19File(FIRMWARE_BL_SIGNED)

		if not os.path.exists(SCP_OUT_DIR):
			os.makedirs(SCP_OUT_DIR)

		os.system(SESSION_BUILD_EXE)

		genPacketDotList(SCP_OUT_DIR)

		if not(zipDir(SCP_OUT_DIR_NAME, outPutFIle)):
			print("Can't generate zip")
		return (firmwarePath, outPutFIle)

	return (firmwarePath, FIRMWARE_BL_SIGNED)

def retKeyName(userInput):
	if not(userInput.endswith('.pem')):
		userInput += '.pem'
	return userInput

def generateECKey(keyname, keypass=""):
	private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())

	if keypass == "":
		serialized_private = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				# encryption_algorithm=serialization.BestAvailableEncryption(b'1234')
				encryption_algorithm=serialization.NoEncryption()
			)
	else:
		serialized_private = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.BestAvailableEncryption(str.encode(keypass))
			)

	# Append .pem if it is missing
	keyname = retKeyName(keyname)

	with open(keyname, "wb") as f:
		f.write(serialized_private)

	# return basename of keyname only
	keyname = retKeyName(os.path.basename(keyname))

	return keyname

def msgGetText(MainWindow, title, value):
	text, ok = QInputDialog.getText(MainWindow, title, value)
	if ok:
		return text
	return None

def msgBoxQuestion(MainWindow, title, message):
	reply = QMessageBox.question(MainWindow, title,
					 message, QMessageBox.Yes, QMessageBox.No)

	if reply == QMessageBox.Yes:
		return True
	else:
		return False

def msgBoxInfo(title, message):
	msg = QMessageBox()
	msg.setWindowTitle(title)
	msg.setIcon(QMessageBox.Information)
	msg.setText(message)
	msg.setStandardButtons(QMessageBox.Ok)
	msg.exec_()

def msgBoxError(title, message, informative="", detail=""):
	msg = QMessageBox()
	msg.setIcon(QMessageBox.Critical)
	msg.setText(message)
	msg.setInformativeText(informative)
	msg.setWindowTitle(title)
	if detail != "":
		msg.setDetailedText(detail)
	msg.setStandardButtons(QMessageBox.Ok)
	msg.exec_()

class programSettings(dict):
	# Override init function.
	def __init__(self, console=None):
		# Call super class init function.
		dict.__init__(self)
		self.console = console

	def ReadFile(self, filename=None):
		if filename==None:
			filename = '.config.json'
		try:
			# Open file.
			with open(filename, 'r') as f:
				file_content = f.read()
				file_content.strip()
				file_settings = json.loads(file_content)
				for setting in file_settings:
					self[setting] = file_settings[setting]
		except IOError:
			if self.console != None:
				self.console.addLine("No settings file found. Using defaults.")

	def AbsoluteImagePath(self, filename):
		return CURRENT_DIR + self['IMAGE_DIR'] + filename

class ButtonPathChoose(QPushButton):

	def __init__(self, *args, **kwargs):
		QPushButton.__init__(self, *args, **kwargs)
		self.edit = None

	def SetEditWidget(self, edit_object):
		self.edit = edit_object

	def GetEditWidget(self):
		return self.edit

class MainGui(mainwindow_gui_auto.Ui_MainWindow):

	def __init__(self, MainWindow):
		self.settings = programSettings()
		self.settings.ReadFile('.config.json')

		# Let the autogenerate script init the UI
		self.setupUi(MainWindow)

		# Manual change the UI settings
		self.MainWindow = MainWindow
		self.MainWindow.setWindowTitle(WINDOWS_TITLE)

		self.initHandler()

	def initHandler(self):
		self.btnSignFirmware.clicked.connect(self.signFirmwareHandler)
		self.btnSignChooseFirmwarePath.clicked.connect(self.showFileDialog)
		self.btnSignChoosePrivateKeyPath.clicked.connect(self.showFileDialog)
		self.btnGenKeys.clicked.connect(self.generateKeyHandler)
		self.actionAbout.triggered.connect(self.AboutWindowHandler)

	def generateKeyHandler(self):
		# validate the input
		if self.editPriKeyPassphrase.text() != self.editPriKeyPassphraseConfirm.text():
			msgBoxError("Error", "Input error:", "Password mismatch")
			return
		if self.editPriKeyName == "":
			msgBoxError("Error", "Input error:", "Private key name is required")
			return

		# generate the key
		outputFolder = str(QFileDialog.getExistingDirectory(self.MainWindow, "Select output Directory"))
		if outputFolder == "":
			return
		outputFile = outputFolder + os.sep + os.path.basename(self.editPriKeyName.text())

		if os.path.isfile(retKeyName(outputFile)):
			if msgBoxQuestion(self.MainWindow,
							"Warning",
							'"%s" already exists, overwrite ?' % retKeyName(self.editPriKeyName.text())
				) is False:
				return

		try:
			keyname = generateECKey(outputFile, str(self.editPriKeyPassphrase.text()))
		except Exception as inst:
			print(sys.exc_info()[0])
			print(type(inst))
			print(type(str(inst)))
			msgBoxError("Error", "Key generate error:", str(inst))
			return

		# response to UI
		msgBoxInfo("Success", 'Private key "%s" successfully generated' % keyname)
		return

	def signFirmwareHandler(self):
		# validate the input
		if self.radBtnSuriBl.isChecked():
			firmwareType = "SURIBL"
		elif self.radBtnSurisdk.isChecked():
			firmwareType = "SURISDK"
		else:
			msgBoxError("Error", 'Please choose one type of firmware')
			return

		if not(os.path.isfile(self.editSignKeyPath.text())):
			msgBoxError("Error", 'Private key "%s" not found' % self.editSignKeyPath.text())
			return

		if not(os.path.isfile(self.editFirmwarePath.text())):
			msgBoxError("Error", 'Firmware "%s" not found' % self.editFirmwarePath.text())
			return

		keyPass = None
		if checkPriKeyEncrypted(self.editSignKeyPath.text()) == True:
			keyPass = msgGetText(self.MainWindow, "Warning", "Please enter private key's passphrase")
			if keyPass is None:
				msgBoxError("Error", "Private key's passphrase is required")
				return

		# sign the firmware
		outputFolder = str(QFileDialog.getExistingDirectory(self.MainWindow, "Select output Directory"))
		if outputFolder == "":
			return

		try:
			ret = signFirmware(self.editSignKeyPath.text(), keyPass, self.editFirmwarePath.text(), outputFolder, firmwareType)
		except Exception as inst:
			# mapping exception from internal library for "human" language
			error_mapping = {
				"unserialize key data": "Passphrase is incorrect",
			}
			error = str(inst)
			for key in error_mapping:
				if str(inst).find(key) != -1:
					error = error_mapping[key]

			# Notify to user
			msgBoxError("Error", "Sign firmware error:", error)
			return

		if ret == None:
			return

		# response to UI
		msgBoxInfo("Success", 'Firmware "%s" successfully signed\n\nOutput: "%s"' % (os.path.basename(ret[0]), os.path.basename(ret[1])))
		return

	def showFileDialog(self):
		button_editline_maping = {
			self.btnSignChooseFirmwarePath: self.editFirmwarePath,
			self.btnSignChoosePrivateKeyPath: self.editSignKeyPath
		}
		sending_button = self.MainWindow.sender()
		fname = QFileDialog.getOpenFileName(self.MainWindow, 'Open file', '.' + os.sep)

		if not(sending_button in button_editline_maping):
			return

		if fname[0]:
			edit_widget = button_editline_maping[sending_button]
			edit_widget.setText(fname[0])
			print (fname)

	def AboutWindowHandler(self):
		app_version_str = '%d.%d.%d' % (APP_VERSION_MAJOR, APP_VERSION_MINOR, APP_VERSION_REV)
		msgBoxInfo("Info", '%s\nVersion: %s' %(WINDOWS_TITLE, app_version_str))
		return

def main():
	app = QApplication(sys.argv)
	MainWindow = QMainWindow()
	auto_ui = MainGui(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())

def main_test():
	app = QApplication(sys.argv)
	MainWindow = QMainWindow()
	ui = mainwindow_gui_auto.Ui_MainWindow()
	ui.setupUi(MainWindow)
	MainWindow.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
	# main_test()
