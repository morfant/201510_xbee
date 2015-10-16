#!/user/bin/python

import time
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


msg = "2" #set data 

while True:
    wiringpi2.serialPuts(serial, msg)
    print(msg)
    time.sleep(0.1) #wait 0.1 sec

wiringpi2.serialClose(serial)
