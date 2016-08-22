#!/usr/bin/python
import base64
from Crypto.Cipher import DES3
from Crypto import Random

BS = 16

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

def CryptoTDESTestMode(string, plaintext, key, iv, mode, fileOutName, secret = None, segment_size = None):
	print "\r\n\r\n"
	print "\t" + string
	
	# Encryption
	if iv is not None and secret is None and segment_size is None:
		encryption_suite = DES3.new(key, mode, iv)
	elif segment_size is not None:
		encryption_suite = DES3.new(key, mode, iv, segment_size=segment_size)
	else:
		encryption_suite = DES3.new(key, mode)
	cipher_text = encryption_suite.encrypt(myPad(plaintext))

	print "testPad           : " + str(len(myPad(plaintext))) 	+ myPad(plaintext)

	newFileByteArray = bytearray(cipher_text)
	print "Len of cipher_text: " + str(len(newFileByteArray))

	newfile=open(fileOutName, 'wb')
	newfile.write(newFileByteArray)

	# Decryption
	if iv is not None and secret is None and segment_size is None:
		decryption_suite = DES3.new(key, mode, iv)
	elif segment_size is not None:
		decryption_suite = DES3.new(key, mode, iv, segment_size=segment_size)		
	else:	
		decryption_suite = DES3.new(key, mode)
	plaintext_dec = decryption_suite.decrypt(cipher_text)
	base64_enc = base64.b64encode(cipher_text)

	print "plaintext_org : " + plaintext 			+ " --> " + str(len(plaintext))
	print "plaintext_dec : " + plaintext_dec 		+ " --> " + str(len(plaintext_dec))
	print "Test unpad    : " + myUnPad(plaintext) 	+ " --> " + str(len(myUnPad(plaintext)))
	print "base64_enc    : " + base64_enc 			+ " --> " + str(len(base64_enc))
	Conclusion("for: " + string, key, iv, plaintext, cipher_text)

# myInput="Some random 32 byte message, not"
myInput=  "Some random 32 b"
myKey= ''.join(chr(x) for x in [0x5D,0x41,0x40,0x2A,0xBC,0x4B,0x2A,0x76,0xB9,0x71,0x9D,0x91,0x10,0x17,0xC5,0x92,0x28,0xB4,0x6E,0xD3,0xC1,0x11,0xE8,0x51])
myIV= ''.join(chr(x) for x in [0x02,0x90,0x9B,0x1C,0xFB,0x50,0xEA,0x0F])
###################################### DES3 ECB Test ###############################################
CryptoTDESTestMode("DES3 ECB Test", myInput, myKey, None, DES3.MODE_ECB, 'fileOutPy.tdes.ecb.enc')

###################################### DES3 CBC Test ###############################################
CryptoTDESTestMode("DES3 CBC Test", myInput, myKey, myIV, DES3.MODE_CBC, 'fileOutPy.tdes.cbc.enc')

###################################### DES3 CFB Test ###############################################
CryptoTDESTestMode("DES3 CFB Test", myInput, myKey, myIV, DES3.MODE_CFB, 'fileOutPy.tdes.cbc.enc', segment_size=64)

###################################### DES3 OFB Test ###############################################
CryptoTDESTestMode("DES3 OFB Test", myInput, myKey, myIV, DES3.MODE_OFB, 'fileOutPy.tdes.cbc.enc')
