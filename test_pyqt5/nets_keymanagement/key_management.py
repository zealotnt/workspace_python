#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import os
import inspect
from PyQt5.QtWidgets import (QMainWindow, QApplication, QPushButton, QWidget,
	QAction, QTabWidget, QVBoxLayout, QLabel, QLineEdit, QGridLayout,
	QFileDialog)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'
WINDOWS_TITLE = "STYL Key Management"

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

class MainTabWidget(QWidget):

	def __init__(self, parent):
		super(QWidget, self).__init__(parent)
		self.layout = QVBoxLayout(self)

		##################################################################################
		# Initialize tab screen
		##################################################################################
		self.tabs = QTabWidget()
		self.tabGenKey = QWidget()
		self.tabSignFirmware = QWidget()
		self.tabs.resize(300,200)

		##################################################################################
		# Add tabs
		##################################################################################
		self.tabs.addTab(self.tabGenKey, "Key generation")
		self.tabs.addTab(self.tabSignFirmware, "Key signing")


		##################################################################################
		# Create first tab
		##################################################################################
		self.titleKeyName = QLabel('Key name:')
		self.titlePriKeyPassphrase = QLabel('Passphrase:')
		self.titlePriKeyPassphraseConfirm = QLabel('Confirm Passphrase:')

		self.editPriKeyName = QLineEdit()
		self.editPriKeyPassphrase = QLineEdit()
		self.editPriKeyPassphraseConfirm = QLineEdit()

		self.btnGenKeys = QPushButton('Generate', self)
		self.btnGenKeys.clicked.connect(self.signFirmware)

		# Add them into the layout
		self.tabGenKey.layout = QGridLayout()
		self.tabGenKey.layout.setSpacing(4)

		self.tabGenKey.layout.addWidget(self.titleKeyName, 1, 0)
		self.tabGenKey.layout.addWidget(self.titlePriKeyPassphrase, 2, 0)
		self.tabGenKey.layout.addWidget(self.titlePriKeyPassphraseConfirm, 3, 0)

		self.tabGenKey.layout.addWidget(self.editPriKeyName, 1, 1)
		self.tabGenKey.layout.addWidget(self.editPriKeyPassphrase, 2, 1)
		self.tabGenKey.layout.addWidget(self.editPriKeyPassphraseConfirm, 3, 1)

		self.tabGenKey.layout.addWidget(self.btnGenKeys, 4, 1)

		self.tabGenKey.setLayout(self.tabGenKey.layout)

		##################################################################################
		# Create second tab
		##################################################################################
		self.titleSignKeyPath = QLabel('Private key:')
		self.titleFirmwarePath = QLabel('Firmware :')

		self.editSignKeyPath = QLineEdit()
		self.editFirmwarePath = QLineEdit()

		self.btnSignChoosePrivateKeyPath = ButtonPathChoose('Select', self)
		self.btnSignChoosePrivateKeyPath.SetEditWidget(self.editSignKeyPath)
		self.btnSignChoosePrivateKeyPath.clicked.connect(self.showFileDialog)

		self.btnSignChooseFirmwarePath = ButtonPathChoose('Select', self)
		self.btnSignChooseFirmwarePath.SetEditWidget(self.editFirmwarePath)
		self.btnSignChooseFirmwarePath.clicked.connect(self.showFileDialog)

		self.btnSignFirmware = QPushButton('Sign', self)
		self.btnSignFirmware.clicked.connect(self.signFirmware)

		# Place it into windows
		self.tabSignFirmware.layout = QGridLayout()
		self.tabSignFirmware.layout.setSpacing(4)

		self.tabSignFirmware.layout.addWidget(self.titleSignKeyPath, 1, 0)
		self.tabSignFirmware.layout.addWidget(self.editSignKeyPath, 1, 1)
		self.tabSignFirmware.layout.addWidget(self.btnSignChoosePrivateKeyPath, 1, 2)

		self.tabSignFirmware.layout.addWidget(self.titleFirmwarePath, 2, 0)
		self.tabSignFirmware.layout.addWidget(self.editFirmwarePath, 2, 1)
		self.tabSignFirmware.layout.addWidget(self.btnSignChooseFirmwarePath, 2, 2)

		self.tabSignFirmware.layout.addWidget(self.btnSignFirmware, 3, 2)

		self.tabSignFirmware.setLayout(self.tabSignFirmware.layout)


		##################################################################################
		# Add tabs to widget
		##################################################################################
		self.layout.addWidget(self.tabs)
		self.setLayout(self.layout)

	def generateKey(self):
		# validate the input

		# generate the key

		# response to UI

		return

	def signFirmware(self):
		# validate the input

		# sign the firmware

		# response to UI
		return

	def showFileDialog(self):
		sending_button = self.sender()
		fname = QFileDialog.getOpenFileName(self, 'Open file', './')

		if fname[0]:
			edit_widget = sending_button.GetEditWidget()
			edit_widget.setText(fname[0])
			print (fname)

class MainGui(QMainWindow):

	def __init__(self):
		super().__init__()

		self.settings = programSettings()
		self.settings.ReadFile('.config.json')

		self.initUI()


	def initUI(self):
		self.table_widget = MainTabWidget(self)
		self.setCentralWidget(self.table_widget)

		settingAction = QAction(QIcon(self.settings.AbsoluteImagePath('setting.png')), 'Setting', self)
		settingAction.setStatusTip('Open setting window')
		settingAction.triggered.connect(self.OpenFile)

		aboutAction = QAction(QIcon(self.settings.AbsoluteImagePath('About50.png')), 'About', self)
		aboutAction.setStatusTip('About')
		aboutAction.triggered.connect(self.AboutWindow)

		self.statusBar()

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(settingAction)
		aboutMenu = menubar.addMenu('&Help')
		aboutMenu.addAction(aboutAction)

		self.setGeometry(300, 300, 1000, 500)
		self.setWindowTitle(WINDOWS_TITLE)
		self.show()

	def OpenFile(self):
		return

	def AboutWindow(self):
		return

def main():
	app = QApplication(sys.argv)
	main_gui = MainGui()
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
