# Installation
- Install dbus-python:
    + Create a virtual env project
    ```
    export PROJECT_HOME=`pwd`
    mkproject test_dbus
    ```
    + Install missing packages
    ```
    sudo apt-get install libdbus-glib-1-dev \
    python-gi
    ```
    + Link the system's python/gi to virtualenv's gi
    `ln -s /usr/lib/python2.7/dist-packages/gi $VITUALENV/lib/python2.7/site-packages`
    + pip install dbus-python, and deps
    ```
    pip install dbus-python
    pip install gi
    ```

