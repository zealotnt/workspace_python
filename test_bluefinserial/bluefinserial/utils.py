__author__ = 'zealotnt'

import sys
import os
import binascii
import re
import ctypes
import ntpath
import inspect

VERBOSE = 0
EXTRA_VERBOSE = 0

# This function get from
# http://stackoverflow.com/questions/4358285/is-there-a-faster-way-to-convert-an-arbitrary-large-integer-to-a-big-endian-seque/4358429#4358429
PyLong_AsByteArray = ctypes.pythonapi._PyLong_AsByteArray
PyLong_AsByteArray.argtypes = [ctypes.py_object,
							   ctypes.c_char_p,
							   ctypes.c_size_t,
							   ctypes.c_int,
							   ctypes.c_int]

def packl_ctypes(lnum):
	a = ctypes.create_string_buffer(lnum.bit_length()//8 + 1)
	PyLong_AsByteArray(lnum, a, len(a), 0, 1)
	return a.raw


# [Table get from](https://github.com/google/bzip2-rpc/blob/master/crctable.c)
BZ2_crc32Table = [
0x00000000, 0x04c11db7, 0x09823b6e, 0x0d4326d9,
0x130476dc, 0x17c56b6b, 0x1a864db2, 0x1e475005,
0x2608edb8, 0x22c9f00f, 0x2f8ad6d6, 0x2b4bcb61,
0x350c9b64, 0x31cd86d3, 0x3c8ea00a, 0x384fbdbd,
0x4c11db70, 0x48d0c6c7, 0x4593e01e, 0x4152fda9,
0x5f15adac, 0x5bd4b01b, 0x569796c2, 0x52568b75,
0x6a1936c8, 0x6ed82b7f, 0x639b0da6, 0x675a1011,
0x791d4014, 0x7ddc5da3, 0x709f7b7a, 0x745e66cd,
0x9823b6e0, 0x9ce2ab57, 0x91a18d8e, 0x95609039,
0x8b27c03c, 0x8fe6dd8b, 0x82a5fb52, 0x8664e6e5,
0xbe2b5b58, 0xbaea46ef, 0xb7a96036, 0xb3687d81,
0xad2f2d84, 0xa9ee3033, 0xa4ad16ea, 0xa06c0b5d,
0xd4326d90, 0xd0f37027, 0xddb056fe, 0xd9714b49,
0xc7361b4c, 0xc3f706fb, 0xceb42022, 0xca753d95,
0xf23a8028, 0xf6fb9d9f, 0xfbb8bb46, 0xff79a6f1,
0xe13ef6f4, 0xe5ffeb43, 0xe8bccd9a, 0xec7dd02d,
0x34867077, 0x30476dc0, 0x3d044b19, 0x39c556ae,
0x278206ab, 0x23431b1c, 0x2e003dc5, 0x2ac12072,
0x128e9dcf, 0x164f8078, 0x1b0ca6a1, 0x1fcdbb16,
0x018aeb13, 0x054bf6a4, 0x0808d07d, 0x0cc9cdca,
0x7897ab07, 0x7c56b6b0, 0x71159069, 0x75d48dde,
0x6b93dddb, 0x6f52c06c, 0x6211e6b5, 0x66d0fb02,
0x5e9f46bf, 0x5a5e5b08, 0x571d7dd1, 0x53dc6066,
0x4d9b3063, 0x495a2dd4, 0x44190b0d, 0x40d816ba,
0xaca5c697, 0xa864db20, 0xa527fdf9, 0xa1e6e04e,
0xbfa1b04b, 0xbb60adfc, 0xb6238b25, 0xb2e29692,
0x8aad2b2f, 0x8e6c3698, 0x832f1041, 0x87ee0df6,
0x99a95df3, 0x9d684044, 0x902b669d, 0x94ea7b2a,
0xe0b41de7, 0xe4750050, 0xe9362689, 0xedf73b3e,
0xf3b06b3b, 0xf771768c, 0xfa325055, 0xfef34de2,
0xc6bcf05f, 0xc27dede8, 0xcf3ecb31, 0xcbffd686,
0xd5b88683, 0xd1799b34, 0xdc3abded, 0xd8fba05a,
0x690ce0ee, 0x6dcdfd59, 0x608edb80, 0x644fc637,
0x7a089632, 0x7ec98b85, 0x738aad5c, 0x774bb0eb,
0x4f040d56, 0x4bc510e1, 0x46863638, 0x42472b8f,
0x5c007b8a, 0x58c1663d, 0x558240e4, 0x51435d53,
0x251d3b9e, 0x21dc2629, 0x2c9f00f0, 0x285e1d47,
0x36194d42, 0x32d850f5, 0x3f9b762c, 0x3b5a6b9b,
0x0315d626, 0x07d4cb91, 0x0a97ed48, 0x0e56f0ff,
0x1011a0fa, 0x14d0bd4d, 0x19939b94, 0x1d528623,
0xf12f560e, 0xf5ee4bb9, 0xf8ad6d60, 0xfc6c70d7,
0xe22b20d2, 0xe6ea3d65, 0xeba91bbc, 0xef68060b,
0xd727bbb6, 0xd3e6a601, 0xdea580d8, 0xda649d6f,
0xc423cd6a, 0xc0e2d0dd, 0xcda1f604, 0xc960ebb3,
0xbd3e8d7e, 0xb9ff90c9, 0xb4bcb610, 0xb07daba7,
0xae3afba2, 0xaafbe615, 0xa7b8c0cc, 0xa379dd7b,
0x9b3660c6, 0x9ff77d71, 0x92b45ba8, 0x9675461f,
0x8832161a, 0x8cf30bad, 0x81b02d74, 0x857130c3,
0x5d8a9099, 0x594b8d2e, 0x5408abf7, 0x50c9b640,
0x4e8ee645, 0x4a4ffbf2, 0x470cdd2b, 0x43cdc09c,
0x7b827d21, 0x7f436096, 0x7200464f, 0x76c15bf8,
0x68860bfd, 0x6c47164a, 0x61043093, 0x65c52d24,
0x119b4be9, 0x155a565e, 0x18197087, 0x1cd86d30,
0x029f3d35, 0x065e2082, 0x0b1d065b, 0x0fdc1bec,
0x3793a651, 0x3352bbe6, 0x3e119d3f, 0x3ad08088,
0x2497d08d, 0x2056cd3a, 0x2d15ebe3, 0x29d4f654,
0xc5a92679, 0xc1683bce, 0xcc2b1d17, 0xc8ea00a0,
0xd6ad50a5, 0xd26c4d12, 0xdf2f6bcb, 0xdbee767c,
0xe3a1cbc1, 0xe760d676, 0xea23f0af, 0xeee2ed18,
0xf0a5bd1d, 0xf464a0aa, 0xf9278673, 0xfde69bc4,
0x89b8fd09, 0x8d79e0be, 0x803ac667, 0x84fbdbd0,
0x9abc8bd5, 0x9e7d9662, 0x933eb0bb, 0x97ffad0c,
0xafb010b1, 0xab710d06, 0xa6322bdf, 0xa2f33668,
0xbcb4666d, 0xb8757bda, 0xb5365d03, 0xb1f740b4
]

# [CRC32_BZIP get from](http://stackoverflow.duapp.com/questions/4468605/calculate-validate-bz2-bzip2-crc32-in-python?rq=1)
def CRC32_BZIP(dataIn):
	# Init
	crcVar = 0xffffffff
	for cha in list(dataIn):
		crcVar = crcVar & 0xffffffff # Unsigned
		crcVar = ((crcVar << 8) ^ (BZ2_crc32Table[(crcVar >> 24) ^ (ord(cha))]))

	# return hex(~crcVar & 0xffffffff)[2:-1].upper()
	return (~crcVar & 0xffffffff)

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

def print_err_dump(data, desc_str):
	print >> sys.stderr, bcolors.FAIL + desc_str + " " + binascii.hexlify(data) + bcolors.ENDC

def print_ok(text):
	print (bcolors.OKGREEN + text + bcolors.ENDC)


def get_fullpath(file_dir, file_name):
	if file_dir == "":
		return file_name
	if os.name == "posix":
		return file_dir + '/' + file_name
	if os.name == "nt":
		return file_dir + '\\' + file_name

def bytesToBigInt(bytes_list):
	ret = 0
	max_idx = len(bytes_list) - 1
	idx = 0
	for val in bytes_list:
		ret += val << 8*(max_idx - idx)
		idx += 1
	return ret

def bigIntToBytes(big_val):
	# [Ref](http://stackoverflow.com/questions/21017698/converting-int-to-bytes-in-python-3)
	bit_length = (big_val.bit_length() + 7) // 8
	return big_val.to_bytes(bit_length, 'big')

def pythonVer():
	if sys.version_info[0] < 3:
		return 2
	return 3

# If python 2, type(data) should be string
# If python 3, type(data) should be bytes
def dump_hex(data, desc_str="", token=":", prefix="", wrap=0, preFormat=""):
	"""
	data: hex data to be dump
	desc_str: description string, will be print first
	token: the mark to seperated between bytes
	prefix: prefix of bytes
	wrap: number of bytes to be printed before create a new line
	"""
	global gStr
	gStr = ""
	def concat_str(text):
		global gStr
		gStr += text
	def write_and_concat_str(text):
		concat_str(text)
		sys.stdout.write(text)

	varType = ""
	varArray = ""
	postfix = ""
	if preFormat == "C" or preFormat == "c":
		token = ", "
		prefix = "0x"
		wrap = 8
		varType = "uint8_t"
		varArray = "[]"
		postfix = "\r\n\t};\r\n\r\n"
	elif preFormat == "raw":
		token = " "
		prefix = ""
		wrap = 0
		desc_str = '"%s":\r\n' % (desc_str)
		postfix = "\r\n\r\n"
	else:
		postfix = "\r\n\t\t}\r\n\r\n"

	# print desc_str + binascii.hexlify(data)
	if wrap == 0:
		to_write = desc_str + token.join(prefix+"{:02x}".format(ord(c)) for c in data) + "\r\n" + postfix
		write_and_concat_str(to_write)
	else:
		# [Ref](http://stackoverflow.com/questions/734368/type-checking-of-arguments-python)
		if isinstance(data, int):
			data = bigIntToBytes(data)

		count = 0

		write_and_concat_str("%s %s%s = {\r\n\t\t" % (varType, desc_str, varArray))
		for c in data:
			if (count % wrap == 0) and (count != 0) and (wrap != 0):
				write_and_concat_str("\r\n\t\t")
			if pythonVer() == 2:
				to_write = prefix + "{:02x}".format(ord(c)) + token
			else:
				to_write = prefix + "{:02x}".format(c) + token
			write_and_concat_str(to_write)
			count += 1

		write_and_concat_str(postfix)
		sys.stdout.flush()
	ret = gStr
	del gStr
	return ret
# Register another name for the dump_hex function
hex_dump = dump_hex

def GetFileContent(path):
	f = open(path, 'rb')
	return f.read()

def ParseHeaderFileValue(file_path, array_name):
	if os.path.isfile(file_path) == False:
		print ("File doesn't exist ! (" + str(file_path) + ")")
		return None

	try:
		fd = open(file_path, 'rU')
	except Exception as inst:
		print ("Can not open file ! %s " % err)
		return None

	try:
		data = fd.read()
	except Exception as inst:
		print ("Can not read file ! %s" % err)
		return None

	fd.close()

	re_search_str = array_name + r".*\n*{((\n.+)+)\n*};"
	tmpList = re.findall(re_search_str, data)

	if len(tmpList) == 0:
		print ("Can not parse data, Incorrect Format!")
		return None

	tmpStr = str(tmpList[0][0])

	tmpStr = tmpStr.replace('\n', '')

	tmpStr = tmpStr.replace(' ', '')
	tmpStr = tmpStr.replace('\t', '')
	tmpArr = tmpStr.split(',')
	# print tmpArr

	finalArr = []
	for idx, value in enumerate(tmpArr):
		finalArr.append((int(value, 16)))

	new_file_val = ''.join(chr(x) for x in finalArr)

	return new_file_val

def callMethodByString(object, name):
	getattr(object, name)()

def getKeysOfDict(dictionary, token="--", boundary="()"):
	ret = ""
	idx = 0

	if len(boundary) != 2:
		print_err("boundary should have 2 character, 1 for opening and 1 for ending")
		return ""

	for item in dictionary:
		if idx == 0:
			ret += boundary[0]
		if idx != 0:
			ret += " %s " % token
		ret += item
		if idx == len(dictionary) - 1:
			ret += boundary[1]
		idx += 1
	return ret

# This function calculate BigInt from list of bytes, Big Endian order
def CalculateBigInt(bytes_list):
	"""
	bytes_list:
	+ Count be list of number
	+ Update 12/5/2017: could be bytes string (Py2.7)
	"""
	ret = 0
	max_idx = len(bytes_list) - 1
	idx = 0
	for val in bytes_list:
		if isinstance(val, str):
			value = ord(val)
		else:
			value = val
		ret += value << 8*(max_idx - idx)
		idx += 1
	return ret

def TrimZeroes(inputBytes):
	idxNotNull = 0
	for idx, item in enumerate(inputBytes):
		if item != '\x00':
			idxNotNull = idx
			break
	return inputBytes[idxNotNull: ]

def FixedBytes(maxLen, inputBytes):
	"""
	Sometimes, the bignum return from function likes packl_ctypes() has some prefix zeroes
	-> This will make the array bigger than the actual limit size
	-> This function will trim down the zeroes

	This function will also prefix the array with 0x00, if the inputBytes is not enough bytes
	if it is not enough bytes, it will be reject from the device
	"""

	# remove the prefix 0x00 of inputBytes
	idxNotNull = 0
	for idx, item in enumerate(inputBytes):
		if item != '\x00':
			idxNotNull = idx
			break
	inputBytes = inputBytes[idxNotNull: ]

	if len(inputBytes) > maxLen:
		print_err("len(inputBytes) > maxLen (%d > %d), can't prefixed, quit" % (len(inputBytes), maxLen))
		return None
	if len(inputBytes) == maxLen:
		# len is enough, no need to prefix
		return inputBytes

	retVal = ''
	lenPrefix = maxLen - len(inputBytes)
	count = 0
	while count < lenPrefix:
		count += 1
		retVal += '\x00'
	retVal += inputBytes
	return retVal

def ProcessFilePath(path):
	"""
	This function accept a text, and try to convert it to a real path file that python can understand
	+ accept the prefix "file:///" (when user ctrl+c the file, it will have a file protocol in it)
	"""
	if not isinstance(path, str):
		return path
	fileProtocolPrefix = "file:///"
	if path.startswith(fileProtocolPrefix):
		path = path[len(fileProtocolPrefix)-1:]
	return path

def CompressFileWithExtension(extensionStr, filePath):
	"""
	This function will test if the `filePath` has extension of `extensionStr`
	If yes, the function will try compress
	and save the same filename and same folder
	with extension ".tar.xz"

	Ex:
	extensionStr: ".json"
	filePath: "~/xmsdk.json"

	output: "~/xmsdk.tar.xz"
	"""
	if filePath.endswith(extensionStr):
		# strip the .json
		fileOutName = filePath[:len(filePath) - len(extensionStr)] + ".tar.xz"
		tarCmd = "tar -cvf %s -C %s %s" % (fileOutName, os.path.dirname(filePath), ntpath.basename(filePath))
		print(tarCmd)
		# [Ref](http://stackoverflow.com/questions/18681595/tar-a-directory-but-dont-store-full-absolute-paths-in-the-archive)
		ret = os.system(tarCmd)
		if ret != 0:
			print_err("Compress file error, quit")
			return None
		# return the generated file name
		return fileOutName
	else:
		print_err("Input file not .json, ignore compressing")
		return None

# [Ref](http://stackoverflow.com/questions/5067604/determine-function-name-from-within-that-function-without-using-traceback)
MYNAME = lambda: inspect.stack()[1][3]
