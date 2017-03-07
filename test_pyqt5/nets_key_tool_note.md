# To generate UI from `*.ui` file
```bash
# Format
pyuic5 -x <ui-file> -o <py-file>

# For example
pyuic5 -x mainwindow.ui -o mainwindow_gui_auto.py
```

# Generate the link folder to secureROM's folder
```bash
# Link to Casign folder
ln -s /home/zealot/workspace_sirius/secureROM/Host/casign/bin/linux Casign

# Link to session_build folder
ln -s /home/zealot/workspace_sirius/secureROM/Host/session_build/bin/linux session_build
```

# Ref
[Ref-1](http://projects.skylogic.ca/blog/how-to-install-pyqt5-and-build-your-first-gui-in-python-3-4/)

# Misc
```
# Set tab order in `Qt Designer`
[Ref](http://doc.qt.io/qt-4.8/designer-tab-order.html)
- `Edit` menu, `Edit Tab Order`
```
