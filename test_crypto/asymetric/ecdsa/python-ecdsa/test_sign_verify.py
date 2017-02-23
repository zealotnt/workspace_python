from ecdsa import SigningKey

sk = SigningKey.generate() # uses NIST192p
print sk

vk = sk.get_verifying_key()
print vk

signature = sk.sign("message")

print signature
print vk.verify(signature, "message")
