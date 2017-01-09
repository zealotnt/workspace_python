- [Ref](http://elinux.org/Grabserial)

- Example
```bash
grabserial -v -d "/dev/ttyUSB0" -b 115200 -e 10 -t -m "U-Boot 2013.04"
```
+ opens /dev/ttyUSB0 (-d /dev/ttyUSB0)
+ at baud rate 115200 (-b 115200)
+ will capture and display data for 10 seconds (-e 10)
+ putting a timestamp on each line received (-t)
+ and restarting the timestamp at 0 when a line containing "-m "U-Boot 2013.04"" is seen.
+ the '-v' makes grabserial verbose (printing some extra messages before starting.)
