#!/bin/bash

#bash /etc/profile.d/tslib.sh

export LD_LIBRARY_PATH=/opt/qt-5.4.2-sailfish/lib:/usr/lib:/lib
export TSLIB_CONFFILE=/etc/ts.conf
export TSLIB_CALIBFILE=/etc/pointercal
export TSLIB_PLUGINDIR=/usr/lib/ts
export TSLIB_TSEVENTTYPE=INPUT
export TSLIB_FBDEVICE=/dev/fb0
export TSLIB_TSDEVICE=/dev/input/by-path/platform-21a4000.i2c-event
export QT_QPA_GENERIC_PLUGINS=tslib:/dev/input/by-path/platform-21a4000.i2c-event
export QT_QPA_PLATFORM_PLUGIN_PATH=/opt/qt-5.4.2-sailfish/plugins/platforms
export QT_QPA_PLATFORM=linuxfb:fb=/dev/fb0
export QT_PLUGIN_PATH=/opt/qt-5.4.2-sailfish/plugins

if [ -e /dev/input/touchscreen0 ]; then
    TSLIB_TSDEVICE=/dev/input/touchscreen0
    export TSLIB_TSDEVICE
fi

export DBUS_SESSION_BUS_ADDRESS=$(cat /home/root/dbus-session.txt)
export ZEBRA_SCANNER=/dev/ttyACM7

#/home/root/busterminal_demo/CEPASReader

echo $2

$1 $2