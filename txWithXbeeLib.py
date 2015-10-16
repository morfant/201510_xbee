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

# Set remote DIO pin 2 to low (mode 4)
while True:
    try:
        xbee.tx(dest_addr='\xff\xff', data='C0')
        time.sleep(1)
    except KeyboardInterrupt:
        break

ser.close()
"""  
xbee.remote_at(
        dest_addr='\x56\x78',
        command='WR')
        """
