#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import json
import os
import inspect
from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QApplication
from PyQt5.QtGui import QIcon


CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '/'

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

class MainGui(QMainWindow):

	def __init__(self):
		super().__init__()

		self.settings = programSettings()
		self.settings.ReadFile('.config.json')

		self.initUI()


	def initUI(self):
		textEdit = QTextEdit()
		self.setCentralWidget(textEdit)

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

		toolbar = self.addToolBar('Setting')
		toolbar.addAction(settingAction)
		toolbar.addAction(aboutAction)

		self.setGeometry(300, 300, 350, 250)
		self.setWindowTitle('Main window')
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
