#!/user/bin/python

import sys
import OSC
import wiringpi2

serial = wiringpi2.serialOpen('/dev/ttyAMA0', 57600)

if serial < 0:
    print("Unable to open serial device: \n")
    sys.exit()

if wiringpi2.wiringPiSetup() == -1:
    print("Unable to start wiringPi: \n")
    sys.exit()


msg = "hello"
wiringpi2.serialPuts(serial, msg)
print("serial send...")
print(msg)

wiringpi2.serialClose(serial)
