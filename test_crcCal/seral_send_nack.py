import serial

ser = serial.Serial(
        port='/dev/ttymxc3',
        baudrate=921600
)

ser.isOpen()

nack_packet = [0x00, 0x35, 0x01, 0xff, 0xfe]

ser.write(nack_packet)

# python secureROM-Sirius/Host/customer_scripts/lib/serial_sender/send_nack.py