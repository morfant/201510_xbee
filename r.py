#!/user/bin/python

import OSC
import wiringpi2
import sys

serial = wiringpi2.serialOpen('/dev/ttyAMA0', 57600)

if serial < 0:
    print("Unable to open serial device: \n")
    sys.exit()    

if wiringpi2.wiringPiSetup() == -1:
    print("Unable to start wiringPi: \n")
    sys.exit()    

while True:
#    print(wiringpi2.serialDataAvail(serial))
    while wiringpi2.serialDataAvail(serial):
        get = wiringpi2.serialGetchar(serial)
        print(hex(get))

wiringpi2.serialClose(serial)
