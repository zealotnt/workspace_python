# Intro
- [Ref page](https://cryptography.io/en/latest/)
- To install `cryptography` Python packge, using:
```bash
$ sudo apt-get install build-essential libssl-dev libffi-dev python-dev
$ sudo pip install cryptography
```

# Troubleshoot when using cryptography
- Sometimes, `crytography` fail on some API, you should update it: `$ sudo pip install -U cryptography`
- There could be some warning about `insecureplatformwarning`, update: `$ sudo pip install -U urllib3[secure]`
