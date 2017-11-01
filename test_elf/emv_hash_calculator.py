#!/usr/bin/env python

import os, sys, inspect, git
import string, tempfile
def get_git_root():
	CURRENT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + os.sep
	path = CURRENT_DIR
	git_repo = git.Repo(path, search_parent_directories=True)
	git_root = git_repo.git.rev_parse("--show-toplevel")
	return git_root
sys.path.insert(0, get_git_root() + '/test_bluefinserial/bluefinserial')
sys.path.insert(0, get_git_root() + '/test_elf/pyelftools')
from utils import *

from elftools import __version__
from elftools.common.exceptions import ELFError
from elftools.common.py3compat import (
		ifilter, byte2int, bytes2str, itervalues, str2bytes, iterbytes)
from elftools.elf.elffile import ELFFile
from elftools.elf.dynamic import DynamicSection, DynamicSegment
from elftools.elf.enums import ENUM_D_TAG
from elftools.elf.segments import InterpSegment
from elftools.elf.sections import NoteSection, SymbolTableSection
from elftools.elf.gnuversions import (
	GNUVerSymSection, GNUVerDefSection,
	GNUVerNeedSection,
	)
from elftools.elf.relocation import RelocationSection
from elftools.elf.descriptions import (
	describe_ei_class, describe_ei_data, describe_ei_version,
	describe_ei_osabi, describe_e_type, describe_e_machine,
	describe_e_version_numeric, describe_p_type, describe_p_flags,
	describe_sh_type, describe_sh_flags,
	describe_symbol_type, describe_symbol_bind, describe_symbol_visibility,
	describe_symbol_shndx, describe_reloc_type, describe_dyn_tag,
	describe_ver_flags, describe_note
	)
from elftools.elf.constants import E_FLAGS
from elftools.dwarf.dwarfinfo import DWARFInfo
from elftools.dwarf.descriptions import (
	describe_reg_name, describe_attr_value, set_global_machine_arch,
	describe_CFI_instructions, describe_CFI_register_rule,
	describe_CFI_CFA_rule,
	)
from elftools.dwarf.constants import (
	DW_LNS_copy, DW_LNS_set_file, DW_LNE_define_file)
from elftools.dwarf.callframe import CIE, FDE, ZERO

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

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

		self._emvSections = [".emv_ep", ".emv_c2", ".emv_c3", ".emv_agnos", ".emv_kizis", ".emv_sped", ".emv_mw", ".emv_freertos"]

		self._binaryData = binary_data

	def getFlashEntryAddress(self):
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == ".text.init":
				return section['sh_addr']
		return 0

	def getDataSectionOffset(self, sectionName):
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == sectionName + "_data":
				return section['sh_size']
		return 0

	def GetSectionInfo(self, sectionName):
		"""
		ret: (section_binary_address, section_size)
		"""
		for nsec, section in enumerate(self.elffile.iter_sections()):
			if section.name == sectionName:
				return (section['sh_addr'] - self.getFlashEntryAddress(), section['sh_size'] + self.getDataSectionOffset(sectionName))
		return (0, 0)

	def GetBinaryData(self, offset, size):
		return self._binaryData[offset:offset+size]

def GenerateBinaryFile(elfFile, gccPath="/opt/arm-2014.05/bin/"):
	tempDir = tempfile.mkdtemp()
	# tempDir = "./"
	ret = os.system("%sarm-none-eabi-objcopy -O binary %s %s/output.bin" % (gccPath, elfFile, tempDir))
	if ret != 0:
		print_err("Error when call arm-none-eabi-objcopy")
		return None
	return (tempDir + "/output.bin")

def DoHash(binary_data):
	hashEngine = hashes.Hash(hashes.SHA1(), backend=default_backend())
	hashEngine.update(binary_data)
	return hashEngine.finalize()

def main():
	if len(sys.argv) != 2:
		print_err("Invalid argument:")
		sys.exit(-1)

	binaryFile = GenerateBinaryFile(sys.argv[1])
	if not binaryFile:
		sys.exit(-1)

	binaryData = GetFileContent(binaryFile)
	with open(sys.argv[1], 'rb') as file:
		elfParser = EmvElfParser(file, binaryData, sys.stdout)
		for emv_section in elfParser._emvSections:
			(offset, size) = elfParser.GetSectionInfo(emv_section)
			section_data = elfParser.GetBinaryData(offset, size)
			sys.stdout.write ("%-17.17s: offset=%10s , size=%-6.6s, hash_data=" % (emv_section, hex(offset), hex(size)))
			dump_hex(DoHash(section_data))

if __name__ == "__main__":
	main()
