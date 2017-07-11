#!/usr/bin/python
import base64
from Crypto.Cipher import DES3
from Crypto import Random

BS = 16

myInput="Hello world !!!!"
myKey= ''.join(chr(x) for x in [0x5D,0x41,0x40,0x2A,0xBC,0x4B,0x2A,0x76,0xB9,0x71,0x9D,0x91,0x10,0x17,0xC5,0x92,0x28,0xB4,0x6E,0xD3,0xC1,0x11,0xE8,0x51])
myIV= ''.join(chr(x) for x in [0x02,0x90,0x9B,0x1C,0xFB,0x50,0xEA,0x0F])

def myPad(s):
	s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
	return s
def myUnPad(s):
	s[:-ord(s[len(s)-1:])]
	return s


###################################### DES3 ECB Test ###############################################
print "\r\n\r\n\t DES3 ECB Test"
# Encryption
encryption_suite = DES3.new(myKey, DES3.MODE_ECB)
cipher_text = encryption_suite.encrypt(myPad(myInput))

print "testPad           : " + str(len(myPad(myInput))) 	+ myPad(myInput)

newFileByteArray = bytearray(cipher_text)
print "Len of cipher_text: " + str(len(newFileByteArray))

newfile=open('fileOutPy.tdes.ecb.enc', 'wb')
newfile.write(newFileByteArray)

# Decryption
decryption_suite = DES3.new(myKey, DES3.MODE_ECB)
plain_text = decryption_suite.decrypt(cipher_text)
base64_enc = base64.b64encode(plain_text)

print "plain_text : " + str(len(plain_text))			+ plain_text
print "Test unpad : " + str(len(myUnPad(plain_text))) 	+ myUnPad(plain_text)
print "base64_enc : " + str(len(cipher_text))			+ base64_enc



###################################### DES3 CBC Test ###############################################
print "\r\n\r\n\t DES3 CBC Test"
# Encryption
encryption_suite = DES3.new(myKey, DES3.MODE_CBC, myIV)
cipher_text = encryption_suite.encrypt(myPad(myInput))

print "testPad           : " + str(len(myPad(myInput))) 	+ myPad(myInput)

newFileByteArray = bytearray(cipher_text)
print "Len of cipher_text: " + str(len(newFileByteArray))

newfile=open('fileOutPy.tdes.cbc.enc', 'wb')
newfile.write(newFileByteArray)

# Decryption
decryption_suite = DES3.new(myKey, DES3.MODE_CBC, myIV)
plain_text = decryption_suite.decrypt(cipher_text)
base64_enc = base64.b64encode(plain_text)

print "plain_text : " + str(len(plain_text))			+ plain_text
print "Test unpad : " + str(len(myUnPad(plain_text))) 	+ myUnPad(plain_text)
print "base64_enc : " + str(len(cipher_text))			+ base64_enc

###################################### DES3 CFB Test ###############################################
print "\r\n\r\n\t DES3 CFB Test"
# Encryption
encryption_suite = DES3.new(myKey, DES3.MODE_CFB, myIV)
cipher_text = encryption_suite.encrypt(myPad(myInput))

print "testPad           : " + str(len(myPad(myInput))) 	+ myPad(myInput)

newFileByteArray = bytearray(cipher_text)
print "Len of cipher_text: " + str(len(newFileByteArray))

newfile=open('fileOutPy.tdes.cfb.enc', 'wb')
newfile.write(newFileByteArray)

# Decryption
decryption_suite = DES3.new(myKey, DES3.MODE_CFB, myIV)
plain_text = decryption_suite.decrypt(cipher_text)
base64_enc = base64.b64encode(cipher_text)

print "plain_text : " + str(len(plain_text))			+ plain_text
print "Test unpad : " + str(len(myUnPad(plain_text))) 	+ myUnPad(plain_text)
print "base64_enc : " + str(len(base64_enc))			+ base64_enc



###################################### DES3 OFB Test ###############################################
print "\r\n\r\n\t DES3 OFB Test"
# Encryption
encryption_suite = DES3.new(myKey, DES3.MODE_OFB, myIV)
cipher_text = encryption_suite.encrypt(myPad(myInput))

print "testPad           : " + str(len(myPad(myInput))) 	+ myPad(myInput)

newFileByteArray = bytearray(cipher_text)
print "Len of cipher_text: " + str(len(newFileByteArray))

newfile=open('fileOutPy.tdes.ofb.enc', 'wb')
newfile.write(newFileByteArray)

# Decryption
decryption_suite = DES3.new(myKey, DES3.MODE_OFB, myIV)
plain_text = decryption_suite.decrypt(cipher_text)
base64_enc = base64.b64encode(cipher_text)

print "plain_text : " + str(len(plain_text))			+ plain_text
print "Test unpad : " + str(len(myUnPad(plain_text))) 	+ myUnPad(plain_text)
print "base64_enc : " + str(len(base64_enc))			+ base64_enc
