#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# System packages
import sys
import json
import os
import inspect
import zipfile
import glob
import shutil

SHORCUT_NAME 		= "styl_key_man.bat"
CURRENT_DIR 		= os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep

shortcutFilePath = os.path.expanduser(("~%sDesktop%s" % (os.sep, os.sep)) + SHORCUT_NAME)
keyManScriptPath = CURRENT_DIR + "key_management.py"

with open(shortcutFilePath, "w") as f:
	f.write("python " + keyManScriptPath)
	f.close()
