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
import mainwindow_gui_auto

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
		self.btnSignFirmware.clicked.connect(self.signFirmware)
		self.btnSignChooseFirmwarePath.clicked.connect(self.showFileDialog)
		self.btnSignChoosePrivateKeyPath.clicked.connect(self.showFileDialog)
		self.btnGenKeys.clicked.connect(self.signFirmware)

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
