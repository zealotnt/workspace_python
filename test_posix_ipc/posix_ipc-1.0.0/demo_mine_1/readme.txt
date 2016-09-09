This example use the posix message queue with the minimal step

# sender.py
It create a message queue (if not created yet), then send a "hello world" string to it

# receiver.py
It open a message queue, and receive the message in it

# To build c source:
```
/opt/eldk-5.5.3/armv7a-hf/sysroots/i686-eldk-linux/usr/bin/arm-linux-gnueabi/arm-linux-gnueabi-gcc sender.c -o sender.c.app -lrt

/opt/eldk-5.5.3/armv7a-hf/sysroots/i686-eldk-linux/usr/bin/arm-linux-gnueabi/arm-linux-gnueabi-gcc receiver.c -o receiver.c.app -lrt
```