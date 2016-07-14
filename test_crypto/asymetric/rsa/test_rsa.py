# http://www.laurentluce.com/posts/python-and-cryptography-with-pycrypto/

from Crypto.PublicKey import RSA
from Crypto import Random

random_generator = Random.new().read
key = RSA.generate(1024, random_generator)

public_key = key.publickey()
enc_data = public_key.encrypt('abcdefgh', 32)
print enc_data

dec_data = key.decrypt(enc_data)
print dec_data