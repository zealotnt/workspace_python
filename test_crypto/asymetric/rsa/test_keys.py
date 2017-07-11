from Crypto.PublicKey import RSA
from Crypto.PublicKey import RSA
import sys

def printHexForm(value):
	print "\tHexform: " + str(hex(value))
	print
	return

def dumpRSAKeyInfo(key):
	print '''
	*****************************
	Public part of key
	*****************************
	'''
	print "\tModulus of key: " + str(key.n)
	print "\tExponent of key: " + str(key.e)
	print '''
	*****************************
	Private part of key
	*****************************
	'''
	print "\tExponent of key: " + str(key.d)
	print "\tFirst factor of key: " + str(key.p)
	print "\tSecond factor of key: " + str(key.q)
	print "\tCRT coefficient of key: " + str(key.u)
	return

key = RSA.generate(2048)
# export private key
f = open('mykey.pri.pem','w')
f.write(key.exportKey('PEM'))
f.close()
# export public key
pubkey = key.publickey()
f = open('mykey.pub.pem','w')
f.write(pubkey.exportKey('PEM'))
f.close()

# Check private key
f = open('mykey.pri.pem','r')
written_key_pri = RSA.importKey(f.read())

print written_key_pri
dumpRSAKeyInfo(written_key_pri)
print key == written_key_pri

# Check public key
f = open('mykey.pub.pem','r')
written_key_pub = RSA.importKey(f.read())

print written_key_pub
print pubkey == written_key_pub