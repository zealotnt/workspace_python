#!/usr/bin/python
import base64
import os
import array
from Crypto.Cipher import AES
from Crypto import Random


class Secret(object):
	def __init__(self, secret=None):
		if secret is None: secret = os.urandom(16)
		self.secret = secret
		self.reset()
		printByteArray(bytearray(self.secret), prefix="secret=\t")
	def counter(self):
		for i, c in enumerate(self.current):
			self.current[i] = c + 1
			if self.current: break
		printByteArray(bytearray(self.current.tostring()), prefix="counter:")
		return self.current.tostring()
	def reset(self):
		self.current = array.array('B', self.secret)

def myPad(s):
	s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
	return s

def myUnPad(s):
	s[:-ord(s[len(s)-1:])]
	return s

def printByteArray(array, prefix=None):
	if prefix is not None:
		print prefix + ''.join('{:02x} '.format(x) for x in array) + " --> " + str(len(array)) + " bytes"
	else:
		print ''.join('{:02x} '.format(x) for x in array) + " --> " + str(len(array)) + " bytes"

def Conclusion(string, key, iv, plaintext, ciphertext):
	array_key = bytearray(key)
	if iv is not None:
		array_iv = bytearray(iv)
	array_plain = bytearray(plaintext)
	array_cipher = bytearray(ciphertext)
	print "\r\nConclusion: " + string
	printByteArray(array_key, prefix = "array_key:\t")
	if iv is not None:
		printByteArray(array_iv, prefix = "array_iv:\t")
	printByteArray(array_plain, prefix = "array_plain:\t")
	printByteArray(array_cipher, prefix = "array_cipher:\t")

def CryptoAESTestMode(string, plaintext, key, iv, mode, fileOutName, secret = None, segment_size = None):
	print "\r\n\r\n"
	print "\t" + string

	# Encryption
	if iv is not None and secret is None and segment_size is None:
		encryption_suite = AES.new(key, mode, iv)
	elif secret is not None:
		secret.reset()
		encryption_suite = AES.new(key, mode, counter=secret.counter)
	elif segment_size is not None:
		encryption_suite = AES.new(key, mode, iv, segment_size=segment_size)
	else:
		encryption_suite = AES.new(key, mode)
	cipher_text = encryption_suite.encrypt(myPad(plaintext))

	print "testPad           : " + str(len(myPad(plaintext))) 	+ myPad(plaintext)

	newFileByteArray = bytearray(cipher_text)
	print "Len of cipher_text: " + str(len(newFileByteArray))

	newfile=open(fileOutName, 'wb')
	newfile.write(newFileByteArray)

	# Decryption
	if iv is not None and secret is None and segment_size is None:
		decryption_suite = AES.new(key, mode, iv)
	elif secret is not None:
		secret.reset()
		decryption_suite = AES.new(key, mode, counter=secret.counter)
	elif segment_size is not None:
		decryption_suite = AES.new(key, mode, iv, segment_size=segment_size)		
	else:
		decryption_suite = AES.new(key, mode)

	plaintext_dec = decryption_suite.decrypt(cipher_text)
	base64_enc = base64.b64encode(cipher_text)

	print "plaintext_org : " + plaintext 			+ " --> " + str(len(plaintext))
	print "plaintext_dec : " + plaintext_dec 		+ " --> " + str(len(plaintext_dec))
	print "Test unpad    : " + myUnPad(plaintext) 	+ " --> " + str(len(myUnPad(plaintext)))
	print "base64_enc    : " + base64_enc 			+ " --> " + str(len(base64_enc))
	Conclusion("for: " + string, key, iv, plaintext, cipher_text)


BS = 16

# myInput="Hello world !!!!"
# myInput="Some random 32 byte message, not"
myInput="Some random 32 b"
# myInput= ''.join(chr(x) for x in [0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21, 0x48, 0x65, 0x6C, 0x6C, 0x6F, 0x20, 0x77, 0x6F, 0x72, 0x6C, 0x64, 0x20, 0x21, 0x21, 0x21, 0x21])

myKey= ''.join(chr(x) for x in [0x5D,0x41,0x40,0x2A,0xBC,0x4B,0x2A,0x76,0xB9,0x71,0x9D,0x91,0x10,0x17,0xC5,0x92,0x28,0xB4,0x6E,0xD3,0xC1,0x11,0xE8,0x51,0x02,0x90,0x9B,0x1C,0xFB,0x50,0xEA,0x0F])
# myKey= ''.join(chr(x) for x in [0x5D,0x41,0x40,0x2A,0xBC,0x4B,0x2A,0x76,0xB9,0x71,0x9D,0x91,0x10,0x17,0xC5,0x92,0x28,0xB4,0x6E,0xD3,0xC1,0x11,0xE8,0x51])

myIV= ''.join(chr(x) for x in [0xDE,0x37,0x08,0x5F,0x7E,0xDA,0x37,0x11,0xFA,0x2D,0x9F,0xE7,0xE0,0xFC,0x29,0xBE])

CryptoAESTestMode("AES ECB Test", myInput, myKey, None, AES.MODE_ECB, "fileOutPy.aes.ecb.enc")
# CryptoAESTestMode("AES CBC Test", myInput, myKey, myIV, AES.MODE_CBC, "fileOutPy.aes.cbc.enc")
# CryptoAESTestMode("AES OFB Test", myInput, myKey, myIV, AES.MODE_OFB, "fileOutPy.aes.ofb.enc")
# CryptoAESTestMode("AES CFB Test with segment=8", myInput, myKey, myIV, AES.MODE_CFB, "fileOutPy.aes.cfb.enc", segment_size=8)
# CryptoAESTestMode("AES CFB Test with segment=128", myInput, myKey, myIV, AES.MODE_CFB, "fileOutPy.aes.cfb.enc", segment_size=128)
# CryptoAESTestMode("AES CFB Test with segment=64", myInput, myKey, myIV, AES.MODE_CFB, "fileOutPy.aes.cfb.enc", segment_size=64)
# CryptoAESTestMode("AES ECB with IV", myIV, myKey, None, AES.MODE_ECB, "fileOutPy.aes.ecb.enc")

# secret = Secret()
# secret = Secret(secret=[0x00 for i in range(16)])
# CryptoAESTestMode("AES CTR Test", myInput, myKey, myIV, AES.MODE_CTR, "fileOutPy.aes.ctr.enc", secret)
