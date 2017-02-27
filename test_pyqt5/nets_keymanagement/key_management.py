#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# System packages
import sys
import json
import os
import inspect

# Qt packages
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
	QAction, QTabWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout,
	QFileDialog, QMessageBox)
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
CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'
WINDOWS_TITLE = "STYL Key Management"


RAW_KEY_FILE			= CURRENT_DIR + "firmware_sign_key.raw"
CASIGN_INI_FILE			= CURRENT_DIR + "ca_sign_build.ini"
SESSION_BUILD_INI_FILE 	= CURRENT_DIR + "session_build.ini"
SB_SCRIPT_FILE 			= CURRENT_DIR + "sb_script.txt"
BINARY_S19_FILE_NAME	= "binary.s19"
BINARY_S19_FILE 		= CURRENT_DIR + BINARY_S19_FILE_NAME
SB_SCRIPT_CONTENT 		= "write-file %s" % (BINARY_S19_FILE_NAME)
SCP_OUT_DIR				= CURRENT_DIR + "scp_out"

def genS19File(binPath):
	command = 'objcopy -I binary -O srec --srec-forceS3 --srec-len=128 --adjust-vma 0x10000000 %s %s' % (binPath, BINARY_S19_FILE)
	os.system(command)

def signFirmware(keyPath, firmwarePath, firmwareType):
	casign_ini_file = {
		"algo": "ecdsa",
		"ecdsa_file": "Casign/crk_ecdsa_angela_test.key",
		"ca": "Casign/suribootloader.bin",
		"sca": "Casign/suribootloader.signed.bin",
		"load_address": "10000000",
		"jump_address": "10000020",
		"arguments": "",
		"application_version": "010A0B03",
		"verbose": "yes"
	}
	session_ini_file = {
		"session_mode": "SCP_ANGELA_ECDSA",
		"verbose": "no",
		"output_file": "%s/out" % (SCP_OUT_DIR),
		"pp": "ECDSA",
		"addr_offset": "00000000",
		"chunk_size": "4094",
		"script_file": "sb_script.txt",
		"ecdsa_file": "session_build/maximtestcrk.key"
	}
	# Check the validity of private key

	# Generate the raw value of private key

	# Write the "ca_sign_build.ini" file
	with open(CASIGN_INI_FILE, "w") as f:
		for item in casign_ini_file:
			print(item, casign_ini_file[item])
			f.write("%s=%s\n" % (item, casign_ini_file[item]))
		f.close()

	# Sign the firmware with Casign
	if firmwareType == "SURIBL":
		# Sign with full param
		os.system('./Casign/ca_sign_build.exe')
		pass
	elif firmwareType == "SURISDK":
		# Sign without the 32bytes header
		return
	else:
		msgBoxError("Error", "Unregcognize firmware type: %s" % firmwareType)
		return

	# Generate the SCP packets if the firmware is bootloader
	if firmwareType == "SURIBL":
		with open(SB_SCRIPT_FILE, "w") as f:
			f.write("%s\n" % SB_SCRIPT_CONTENT)
			f.close()

		with open(SESSION_BUILD_INI_FILE, "w") as f:
			for item in session_ini_file:
				print(item, session_ini_file[item])
				f.write("%s=%s\n" % (item, session_ini_file[item]))
			f.close()

		genS19File(firmwarePath)

		if not os.path.exists(SCP_OUT_DIR):
			os.makedirs(SCP_OUT_DIR)

		os.system('./session_build/session_build.exe')
		return

	# Generate the sign firmware if the firmware is surisdk

	return

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

	if not(keyname.endswith('.pem')):
		keyname += '.pem'

	with open(keyname, "wb") as f:
		f.write(serialized_private)

	return keyname

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
		self.btnGenKeys.clicked.connect(self.generateKey)

	def generateKey(self):
		# validate the input
		if self.editPriKeyPassphrase.text() != self.editPriKeyPassphraseConfirm.text():
			msgBoxError("Error", "Input error:", "Password mismatch")
			return
		if self.editPriKeyName == "":
			msgBoxError("Error", "Input error:", "Private key name is required")
			return

		# generate the key
		try:
			keyname = generateECKey(str(self.editPriKeyName.text()), str(self.editPriKeyPassphrase.text()))
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
		if not(os.path.isfile(self.editSignKeyPath.text())):
			msgBoxError("Error", 'Private key "%s" not found' % self.editSignKeyPath.text())
			return

		if not(os.path.isfile(self.editFirmwarePath.text())):
			msgBoxError("Error", 'Firmware "%s" not found' % self.editFirmwarePath.text())
			return

		# sign the firmware
		signFirmware(self.editSignKeyPath.text(), self.editFirmwarePath.text(), "SURIBL")

		# response to UI
		msgBoxInfo("Success", 'Firmware "%s" successfully signed' % self.editFirmwarePath.text())
		return

	def showFileDialog(self):
		button_editline_maping = {
			self.btnSignChooseFirmwarePath: self.editPriKeyName,
			self.btnSignChoosePrivateKeyPath: self.editSignKeyPath
		}
		sending_button = self.MainWindow.sender()
		fname = QFileDialog.getOpenFileName(self.MainWindow, 'Open file', './')

		if not(sending_button in button_editline_maping):
			return

		if fname[0]:
			edit_widget = button_editline_maping[sending_button]
			edit_widget.setText(fname[0])
			print (fname)

	def AboutWindow(self):
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
