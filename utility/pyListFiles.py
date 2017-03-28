#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-03-28 11:25:47

import glob
import os
import sys
from optparse import OptionParser, OptionGroup


BASH_HEADER="""
#!/bin/bash

"""

if __name__ == "__main__":
	parser = OptionParser()

	parser.add_option(  "-p", "--path",
						dest="path",
						type="string",
						help="specified path to the directory to be listed recursively")
	parser.add_option(  "-r", "--root",
						dest="root",
						action="store_true",
						default=False,
						help="If specified, the output folder will be from root: /")
	parser.add_option(  "-s", "--script",
						dest="delete_script",
						help="If specified, this script will generate the bash script "\
						"to help remove all the file list in the system")
	parser.add_option(  "-d", "--debug",
						dest="debug",
						action="store_true",
						default=False,
						help="Print the result to stdout when done")

	(options, args) = parser.parse_args()

	if options.path is None:
		parser.print_help()
		sys.exit(-1)

	listPath = options.path
	isGenScript = False if (options.delete_script is None) else True
	nameGenScript = ""
	contentGenScript = BASH_HEADER

	if isGenScript == True:
		if not(options.delete_script.endswith('.sh')):
			nameGenScript = options.delete_script + '.sh'
		else:
			nameGenScript = options.delete_script

	for filename in glob.iglob(listPath + '/**/*', recursive=True):
		if os.path.isdir(filename):
			continue

		if options.root is True:
			# remove the prefix path
			# the first character of path should be '/'
			filename = '/' + filename[len(listPath):]
		contentGenScript += "rm %s\n" % filename

	if isGenScript:
		with open(nameGenScript, "w") as f:
			f.write(contentGenScript)
			f.close()

	if options.debug:
		print(contentGenScript)
