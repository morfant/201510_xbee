#!/user/bin/python

import OSC
import wiringpi2
import sys

#serial
serial = wiringpi2.serialOpen('/dev/ttyAMA0', 57600)

if serial < 0:
    print("Unable to open serial device: \n")
    sys.exit()    

if wiringpi2.wiringPiSetup() == -1:
    print("Unable to start wiringPi: \n")
    sys.exit()    

i = 0
length = 0
rssi = 0
 
while True:
#    print(wiringpi2.serialDataAvail(serial))
    while wiringpi2.serialDataAvail(serial):
        get = wiringpi2.serialGetchar(serial)
        
        if get == 0x7e:
            i = 0
            print("\nBtye started")

        if i == 2:
            length = get
            print("length: ", length)
        if i == 6:
            rssi = get
            print("rssi: ", rssi)
        if i == 8:
            data = get
            print("data: ", data)

        i = i + 1
            
wiringpi2.serialClose(serial)
