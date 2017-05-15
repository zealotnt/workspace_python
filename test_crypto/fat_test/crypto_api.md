# Introduction
This document show instruction and API implementation, API guide for cryptography item on STT.

# New API:
## 1.  True Random Number Generator (TRNG)

### 1.1 Command format

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0e |
| Number of Byte | 1 | Number of bytes of Random Number to be generated |

### 1.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0f |
| Status Response | 1 | Result code |
| Data | Variable | Random Numbers |

## 2.  TDES hardware cryptography

### 2.1 Command format

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0a |
| Number of Block | 1 | Number of 8-byte block |
| Key Length | 1 | Length of TDES/3DES key |
| Input Data | Variable | Plaintext for encryption, Ciphered text for decryption |
| TDES Key Value | Variable | Could be 8/16/24 bytes |
| IV | 8 | Initial Vector |
| Mode | 1 | Encryption/Decryption Mode<br>0x00: ECB Encryption<br>0x01: ECB Decryption <br>0x02: CBC Encryption <br>0x03: CBC Decryption <br>0x04: OFB Encryption <br>0x05: OFB Decryption <br>0x06: CFB Encryption <br>0x07: CFB Decryption |

### 2.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0b |
| Status Response | 1 | Result code |
| Output Text | Variable | Ciphered Text For encryption<br>Plaintext for decryption |

## 3.  AES hardware cryptography

### 3.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0c |
| Number of Block | 1 | Number of 16-byte block |
| Key Length | 1 | Length of AES key |
| Input Data | Variable | Plaintext for encryption<br>Ciphered text for decryption |
| AES Key Value | Variable | Could be 16/24/32 bytes |
| IV | 8 | Initial Vector |
| Mode | 1 | Encryption/Decryption Mode<br>0x00: ECB Encryption<br>0x01: ECB Decryption<br>0x02: CBC Encryption<br>0x03: CBC Decryption<br>0x04: OFB Encryption<br>0x05: OFB Decryption<br>0x06: CFB Encryption<br>0x07: CFB Decryption |

### 3.2 Reponse message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x0d |
| Status Response | 1 | Result code |
| Output Text | Variable | Ciphered Text For encryption<br>Plaintext for decryption |

## 4.  NIS 800-38B CMAC

### 4.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x44 |
| CMAC-Cipher | 1 | Type of cipher of CMAC operation<br>0x00: TDES <br>0x01: AES |
| Number of Block | 1 | Number of 16-bytes (for AES cipher) or 8-bytes (for TDES cipher) block |
| Key Length | 1 | Length of AES/TDES key<br>8/16/24 bytes for TDES<br>16/24/32 bytes for AES |
| Input Data | Variable | Input message |
| AES/TDES Key Value | Variable | Key value |

### 4.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x45 |
| Status Response | 1 | Result code |
| Output Bytes | Variable | MAC for input message |

- References
    + [Ref-1](https://gist.github.com/ecerulm/90653daf2b808aea0837)
    + [Ref-2](http://stackoverflow.com/questions/28354844/how-to-calculate-aes-cmac-using-openssl)

## 5 Key Download

#### 5.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x46 |
| Tag | 1 | Any value in Tags table |
| Length | 2 | Length of Value field in current TLV block |
| Value | Variable | The data of the corresponding tag |

| Tag  | Length valid | Description |
|----------|:-------------:|:------|
| 0x01 | 1024/2048/3072 bit | p value of DSS parameters |
| 0x02 | 1024/2048/3072 bit | q value of DSS parameters |
| 0x03 | 1024/2048/3072 bit | g value of DSS parameters |
| 0x04 | 1024/2048/3072 bit | y value of DSS public key |
| 0x05 | 1024/2048/3072 bit | x value of DSS private key |
| 0x06 | 256 bit | x point of ECDSA public key |
| 0x07 | 256 bit | y point of ECDSA public key |
| 0x08 | 256 bit | 256 bit of ECDSA private key |
| 0x09 | 2048/3072 bit | n The modulus of RSA public key |
| 0x0A | 2048/3072 bit | d The Private Exponent of RSA private key |
| 0x0B | 4 Bytes | Public exponent of RSA |

#### 5.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x47 |
| Status Response | 1 | Result code |

## 6.  Digital Signature Standard (DSS)

### 6.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x48 |
| Operation | 1 | DSA operation<br>0x00: Sign<br>0x01: Verify |
| Hash Algo | 1 | Hash algorithm<br>0x00: SHA1<br>0x01: SHA256 |
| Input message length | 2 | Length of input message |
| Signature length | 1 | Length of signature<br>Signature length always <= 40 bytes (verify only, if sign, this length = 0) |
| Input message | Variable | Message to be signed/verified |
| Signature | Variable | Signature value (if sign, this field is empty) |


### 6.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x49 |
| Status Response | 1 | Result code |
| Signature/Verify | N | If signing: Signature for input message, N = double of DSA key<br>If verify: result in verify request, N = 1<br>0: valid<br>1: invalid |

- References
    + [DSA Sig len](https://groups.google.com/forum/#!topic/sci.crypt/4iGX27jDJu8)

## 7.  The Elliptic Curve Digital Signature Algorithm (ECDSA)

### 7.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4a |
| Operation | 1 | ECDSA operation<br>0x00: Sign<br>0x01: Verify |
| Curve Param | 1 | ECDSA curve params<br>0x00: SECP256R1 |
| Hash Algo | 1 | Hash algorithm<br>0x00: SHA1<br>0x01: SHA256 |
| Input message length | 2 | Length of input message (Max 300 bytes) |
| Signature length | 1 | Length of signature<br>Length equal to input text box |
| Input message | Variable | Message to be signed/verified |
| Signature | Variable | Signature value (if sign, this is not filled) |

### 7.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4b |
| Status Response | 1 | Result code |
| Signature/Verify | N | If signing: Signature for input message, N = double of curve/key length<br>If verify: Result in verify request, N = 1<br>0: valid<br>1: invalid |

## 8.  RSA cryptography

### 8.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4c |
| Operation | 1 | RSA operation<br>0x00: Encrypt<br>0x01: Decrypt |
| Input message | N | Message to be encrypted/decrypted, N = RSA Key size |

### 8.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4d |
| Status Response | 1 | Result code |
| Output Text | N | N = RSA key size<br>Ciphered Text For encryption<br>Plaintext for decryption |

## 9.  SHA message digests

### 9.1 Command message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4e |
| SHA Algorithm | 1 | Type of SHA operation<br>0x00: SHA1<br>0x01: SHA224<br>0x02: SHA256<br>0x03: SHA384<br>0x04: SHA512 |
| Message | Variable | Input message |

### 9.2 Response message

| Field  | Length (byte) | Value |
|----------|:-------------:|:------|
| Command Code | 1 | Fix value: 0x8b |
| Command Control Code | 1 | Fix value: 0x4f |
| Status Response | 1 | Result code |
| Digest | Variable | Digest of input message<br>SHA1: 20B <br>SHA224: 28B <br>SHA256: 32B<br>SHA384: 48B<br>SHA512: 64B |
