#!/usr/bin/python
# -*- coding: utf-8 -*-
# @Author: zealotnt
# @Date:   2017-06-22 15:47:07

# [API Doc](http://pythonhosted.org/pycrypto/)
# [API Doc 2](https://www.dlitz.net/software/pycrypto/api/current/)
from Crypto.PublicKey import RSA
from Crypto import Random

n = 0xd0b750c8554b64c7a9d34d068e020fb52fea1b39c47971a359f0eec5da0437ea3fc94597d8dbff5444f6ce5a3293ac89b1eebb3f712b3ad6a06386e6401985e19898715b1ea32ac03456fe1796d31ed4af389f4f675c23c421a125491e740fdac4322ec2d46ec945ddc349227b492191c9049145fb2f8c2998c486a840eac4d3
e = 0x859e499b8a186c8ee6196954170eb8068593f0d764150a6d2e5d3fea7d9d0d33ac553eecd5c3f27a310115d283e49377820195c8e67781b6f112a625b14b747fa4cc13d06eba0917246c775f5c732865701ae9349ea8729cde0bbade38204e63359a46e672a8d0a2fd530069
d = 0x27b7119a09edb827c13418c820b522a1ee08de0e4bb28106db6bb91498a3b361ab293af83fefcdd8a6bd2134ca4afacf64a0e33c014f48f47530f8847cc9185cbedec0d9238c8f1d5498f71c7c0cff48dc213421742e34350ca94007753cc0e5a783264cf49ff644ffea94253cfe86859acd2a2276ca4e7215f8ebaa2f188f51
c = 0x6cf87c6a65925df6719eef5f1262edc6f8a0a0a0d21c535c64580745d9a268a95b50ff3be24ba8b649ca47c3a760b71ddc3903f36aa1d98e87c53b3370be784bffcb5bc180dea2acc15bb12e681c889b89b8f3de78050019dcdbb68c051b04b880f0f8c4e855321ffed89767fc9d4a8a27a5d82ba450b2478c21e11843c2f539
k = 0x5c7bce723cf4da053e503147242c60678c67e8c22467f0336b6d5c31f14088cb3d6cefb648db132cb32e95092f3d9bcd1cab51e68bd3a892ab359cdff556785ae06708633d39a0618f9d6d70f6bdeb6b777e7dd9acc41f19560c71a68479c8a07b14fb9a4c765fd292ae56dd2f2143b62649cc70fb604fdc5cc1ade6e29de235

##########################################################################
# begin
##########################################################################
prikey_tup = (n, e, d)
pubkey_tup = (n, e)

public_key = RSA.construct(pubkey_tup)
private_key = RSA.construct(prikey_tup)

self_enc_data = public_key.encrypt(k, 300)
self_dec_data = private_key.decrypt(c)
print (self_dec_data == k)
print (self_enc_data[0] == c)
