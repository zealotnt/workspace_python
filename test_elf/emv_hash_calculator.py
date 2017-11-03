#!/usr/bin/env python

import os, sys, inspect, git
import string, tempfile

from elftools.elf.elffile import ELFFile
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

class bcolors:
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'

def print_err(text):
	print >> sys.stderr, bcolors.FAIL + text + bcolors.ENDC

def dump_hex(data, desc_str="", token=":", prefix="", preFormat=""):
	def write_and_concat_str(text):
		sys.stdout.write(text)

	to_write = desc_str + token.join(prefix+"{:02x}".format(ord(c)) for c in data) + "\r\n"
	write_and_concat_str(to_write)

class EmvElfParser(object):
	""" display_* methods are used to emit output into the output stream
	"""
	def __init__(self, file, binary_data, output):
		""" file:
				stream object with the ELF file to read

			output:
				output stream to write to
		"""
		self.elffile = ELFFile(file)
		self.output = output

		# Lazily initialized if a debug dump is requested
		self._dwarfinfo = None

		self._versioninfo = None

		self._emvSections = [".emv_l1", ".emv_ep", ".emv_c2", ".emv_c3", ".emv_agnos", ".emv_kizis", ".emv_sped", ".emv_mw", ".emv_freertos"]

		self._binaryData = binary_data

	def getFlashEntryAddress(self):
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == ".text.init":
				return section['sh_addr']
		print_err("Can't find .text.init")
		sys.exit(-1)
		return 0

	def getDataSectionOffset(self, sectionName):
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == sectionName + "_data":
				return section['sh_size']
		print_err("Can't find %s" % (sectionName + "_data"))
		sys.exit(-1)
		return 0

	def GetSectionInfo(self, sectionName):
		"""
		ret: (section_binary_address, section_size)
		"""
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == sectionName:
				size = section['sh_size']
				du = 4 - (section['sh_size'] % 4)
				if section['sh_size'] % 4 != 0:
					size = size + 4 - (section['sh_size'] % 4)
				return (section['sh_addr'] - self.getFlashEntryAddress(), size + self.getDataSectionOffset(sectionName), section['sh_size'], du)
		print_err("Can't find %s" % sectionName)
		return (0, 0)

	def GetBinaryData(self, offset, size):
		return self._binaryData[offset:offset+size]

def GenerateBinaryFile(elfFile, gccPath="/opt/arm-2014.05/bin/"):
	# tempDir = tempfile.mkdtemp()
	tempDir = "./"
	ret = os.system("%sarm-none-eabi-objcopy -O binary %s %s/output.bin" % (gccPath, elfFile, tempDir))
	if ret != 0:
		print_err("Error when call arm-none-eabi-objcopy")
		return None
	return (tempDir + "/output.bin")

def DoHash(binary_data):
	hashEngine = hashes.Hash(hashes.SHA1(), backend=default_backend())
	hashEngine.update(binary_data)
	return hashEngine.finalize()

def GetFileContent(path):
	f = open(path, 'rb')
	return f.read()

def main():
	if len(sys.argv) != 2:
		print_err("Invalid argument:")
		print("Usage: python %s <firmware-elf-file>" % os.path.basename(__file__))
		sys.exit(-1)

	binaryFile = GenerateBinaryFile(sys.argv[1])
	if not binaryFile:
		sys.exit(-1)

	binaryData = GetFileContent(binaryFile)
	dump_hex(DoHash(binaryData), "SHA1 of binary firmware: ")
	with open(sys.argv[1], 'rb') as file:
		elfParser = EmvElfParser(file, binaryData, sys.stdout)
		for emv_section in elfParser._emvSections:
			(offset, size, f1, du) = elfParser.GetSectionInfo(emv_section)
			section_data = elfParser.GetBinaryData(offset, size)
			# If the firmware is being debug, the unoccupied flash will be 0xff (while the .bin file will be 0x00)
			# So if you want to compare the hash of debug firmware, enable these following lines
			# if du != 4:
			# 	while du:
			# 		du -= 1
			# 		section_data = section_data[:f1+du] + '\xff' + section_data[f1+1+du:]
			sys.stdout.write ("%-17.17s: offset=%10s , size=%-6.6s, hash_data=" % (emv_section, hex(offset), hex(size)))
			dump_hex(DoHash(section_data))

if __name__ == "__main__":
	main()
