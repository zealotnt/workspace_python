# Installation
```bash
# Install SIP
# + Download at
https://www.riverbankcomputing.com/software/sip/download

# Install PyQt5
# + Download at
https://www.riverbankcomputing.com/software/pyqt/download5

# Extract, configure, install (both SIP and PyQt5 apply these steps)
python configure.py
make
sudo make install

# Note:
# + Error: PyQt5 requires Qt v5.0 or later. You seem to be using v4.8.6. Use the
sudo apt-get install qt5-default

# + pyuic5, ...
sudo apt-get install pyqt5-dev-tools
```

# Nasty stuff when install package with Python3
[Ref](http://askubuntu.com/questions/861265/python-3-importerror-no-module-named-setuptools-ubuntu-14-04-lts)
- Need to build Python3 from source

```bash
# Install package before build
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils

# Install pip (a tool for installing and managing Python packages);
wget https://bootstrap.pypa.io/get-pip.py -O - | sudo python3

# Install setuptools with;
wget https://bootstrap.pypa.io/ez_setup.py -O - | sudo python3
```


# Facts
[Ref](http://zetcode.com/gui/pyqt5/introduction/)
- PyQt5 is available for the Python 2.x and 3.x
- Developers can choose between a GPL and a commercial license.
