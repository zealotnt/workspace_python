#!/bin/bash
CC="/opt/eldk-5.5.3/armv7a-hf/sysroots/i686-eldk-linux/usr/bin/arm-linux-gnueabi/arm-linux-gnueabi-"
dir="/opt/eldk-5.5.3/armv7a-hf/sysroots/i686-eldk-linux/"
#dir=
#CC=
if [ -e "i2cBluefin.so" ];
then
	echo "rm *.so"
	rm *.so
fi
#gcc -fPIC -shared -I /usr/include/python2.7/ -lpython2.7 -o myModule.so myModule.c
"$CC"gcc -fPIC -shared -I "$dir"/usr/include/python2.7/ -o i2cBluefin.so i2cBluefin.c

"$CC"gcc -fPIC -shared -I "$dir"/usr/include/python2.7/ -o printSomething.so printSomething.c

echo "Successful!"
