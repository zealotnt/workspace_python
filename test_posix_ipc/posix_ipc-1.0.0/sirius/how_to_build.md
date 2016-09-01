# Extract python folder to eldk:
- Extract `.../test_pythonCallC/python2.7.zip`
- Copy it to eldk: `cp .../.../test_pythonCallC/python2.7 /opt/eldk-5.5.3/armv7a-hf/sysroots/armv7ahf-vfp-neon-linux-gnueabi/usr/include/`

# Build the lib:
```
cd .../test_posix_ipc/posix_ipc-1.0.0

/opt/eldk-5.5.3/armv7a-hf/sysroots/i686-eldk-linux/usr/bin/arm-linux-gnueabi/arm-linux-gnueabi-gcc -fPIC -shared -I /opt/eldk-5.5.3/armv7a-hf/sysroots/armv7ahf-vfp-neon-linux-gnueabi/usr/include/python2.7 -o posix_ipc.so posix_ipc_module.c -lrt
```

Run the python code, with the library in the same folder