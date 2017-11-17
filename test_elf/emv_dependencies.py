#!/usr/bin/env python

from sys import argv
from io import open
from networkx import MultiDiGraph
import networkx
import re, os, sys
from optparse import OptionParser, OptionGroup

def find_cref(inmap):
	while True:
		l = inmap.readline()
		if l.strip() == 'Cross Reference Table':
			break;
		if len(l) == 0: return False
	while True:
		l = inmap.readline()
		if len(l) == 0: return False
		words = l.split()
		if len(words) == 2:
			if words[0] == 'Symbol' and words[1] == 'File':
				return True

def read_cref(inmap):
	modules = MultiDiGraph()
	while True:
		l = inmap.readline()
		words = l.split()
		if len(words) == 2:
			last_symbol = words[0]
			last_module = words[1]
		elif len(words) == 1:
			modules.add_edge(words[0], last_module, label=last_symbol);
		elif len(l) == 0:
			break
	return modules

class bcolors:
	HEADER = '\033[95m'
	BLUE = '\033[94m'
	GREEN = '\033[92m'
	YELLOW = '\033[93m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def printDeps(user, provider, label):
	toPrint = bcolors.GREEN + bcolors.BOLD + user + bcolors.ENDC +\
		" -> " +\
		bcolors.BLUE + bcolors.BOLD + provider + bcolors.ENDC +\
		" " + bcolors.YELLOW + bcolors.BOLD + label + bcolors.ENDC
	print toPrint

def main():
	parser = OptionParser(
			usage='usage: %prog [options] <map-file>',
			description="This script print the dependencies of emv-modules to non-emv-modules",
			prog=os.path.basename(__file__))
	parser = OptionParser()
	parser.add_option(	"--symbol-once",
						dest="symbol_once",
						action="store_true",
						default=False,
						help="Only print the symbol once, the next occurence will be ignored")
	parser.add_option(	"-s", "--symbol-only",
						dest="symbol_only",
						default="",
						help="Only print selected symbol")
	parser.add_option(	"--ignore-pattern",
						dest="ignore_pattern",
						default="",
						help="Any symbol has prefix similar with this is ignored")
	parser.add_option(	"-f", "--file",
						type="string",
						dest="file_path",
						default="",
						help="Path to .map file")
	(options, args) = parser.parse_args()

	if options.file_path == "":
		print ("Error: file_path is required")
		parser.print_help()
		sys.exit(0)

	filePatterns = [
	r"\./source/styl/mlsEmv/mlsEmvCtlL1/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosEP/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosC2/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosC3/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosACE2P/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosCad/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosDB/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosEMVCo/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosHsm/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosPlatform/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosSdk/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosTestKernel/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosTLV/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosKizis/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosSped/src/[^\.]+\.o",
	r"\./source/styl/mlsEmv/mlsAgnos/mlsAgnosMW/src/[^\.]+\.o",
	r"\./source/styl/mlsOsal/src/[^\.]+\.o",
	r"\./source/styl/mlsOsal/freeRTOS/[^\.]+\.o",
	r"/opt/arm-2014.05/bin/../lib/gcc/arm-none-eabi/4.8.3/../../../../arm-none-eabi/lib/thumb2/libc\.a",
	r"/opt/arm-2014.05/bin/../lib/gcc/arm-none-eabi/4.8.3/thumb2/libgcc.a",
	r"/surisdk/source/maxim/lib/libucl/cortex-m3/libucl-2.5.5_max32550.a",
	]

	results = []

	inmap = open(options.file_path, 'r')

	if find_cref(inmap):
		modules = read_cref(inmap)

		# for user, provider, label in modules.edges(data=True):
		# 	print user, provider, label['label']

		for user, provider, label in modules.edges(data=True):
			isPrinted = False
			countNotMatch = 0
			for pattern1 in filePatterns:
				if isPrinted:
					break
				match1 = re.findall(pattern1, user, re.MULTILINE)
				if len(match1) == 1:
					# print user, provider, label['label']
					for pattern2 in filePatterns:
						if isPrinted:
							break
						match2 = re.findall(pattern2, provider, re.MULTILINE)
						if len(match2) == 0:
							countNotMatch += 1
						if countNotMatch >= len(filePatterns):
							results.append([user, provider, label['label']])
							isPrinted = True

		labelOccur = []
		for result in results:
			user = result[0]
			provider = result[1]
			symbol = result[2]
			ignore = False
			if options.symbol_once:
				for label_check in labelOccur:
					if label_check == symbol:
						ignore = True
						break
			if ignore:
				continue
			if options.symbol_only != "":
				if symbol == options.symbol_only:
					printDeps(user, provider, symbol)
				continue
			if options.ignore_pattern != "":
				if symbol.startswith(options.ignore_pattern):
					continue
			printDeps(user, provider, symbol)
			labelOccur.append(symbol)

		# networkx.drawing.nx_pydot.write_dot(modules, argv[2])

	else:
		print 'error: cross reference table not found.'

if __name__ == "__main__":
	main()
