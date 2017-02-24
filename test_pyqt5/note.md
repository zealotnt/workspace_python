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

# Facts
[Ref](http://zetcode.com/gui/pyqt5/introduction/)
- PyQt5 is available for the Python 2.x and 3.x
- Developers can choose between a GPL and a commercial license.
