#!/usr/bin/env python

from sys import argv
from io import open
from networkx import MultiDiGraph
import networkx
import re

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
	filePatterns = [
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
	]

	inmap = open(argv[1], 'r')

	if find_cref(inmap):
		modules = read_cref(inmap)

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
							printDeps(user, provider, label['label'])
							isPrinted = True

		# networkx.drawing.nx_pydot.write_dot(modules, argv[2])

	else:
		print 'error: cross reference table not found.'

if __name__ == "__main__":
	main()
