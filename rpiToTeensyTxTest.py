#! /usr/bin/python
    
# Import and init an XBee device
from xbee import XBee,ZigBee
import serial
import time

ser = serial.Serial('/dev/ttyAMA0', 57600)

# Use an XBee 802.15.4 device
# To use with an XBee ZigBee device, replace with:
#xbee = ZigBee(ser)
xbee = XBee(ser)


def print_data(data) :
    print "print_data"
    print data

xbee = XBee(ser, callback=print_data)

# Set remote DIO pin 2 to low (mode 4)

i = 0
while True:
    try:
        print i
        xbee.tx(dest_addr='\x2C\x2C', data=str(i%10))
#        xbee.tx(dest_addr='\x1B\x1B', data=str(i%10))
        time.sleep(0.05)
        i = i + 1

    except KeyboardInterrupt:
        break

xbee.halt()
ser.close()
"""  
xbee.remote_at(
        dest_addr='\x56\x78',
        command='WR')
        """
