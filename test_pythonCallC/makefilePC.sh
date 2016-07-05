#!/bin/bash
"$CC"gcc -fPIC -shared -I "$dir"/usr/include/python2.7/ -o printSomething.so printSomething.c
echo "PC Build Successful!"