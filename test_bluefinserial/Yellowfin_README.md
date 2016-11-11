# socat Testing

## To run socat
```bash
sudo socat -d -d pty,link=/dev/ttyv1,echo=0 pty,link=/dev/ttyv2,echo=0
```

## Prerequisities
- xmsdk must be running

## Test
```
cd /home/root/TestSerial
python test_getversion.py
```

# To run `util_time.py`

## Prerequisities
Put the `util_time.py` and `posix_ipc.so` to /home/root

## To get time from RF processor
`python util_time.py -g` the value return is in unix-time-stamp format

## To set time to RF processor
`python util_time.py -s <unix-time-stamp>`

## Combine with linux command, to set time to iMX's date
`date +%s -s @$(python /home/root/util_time.py -g)`
