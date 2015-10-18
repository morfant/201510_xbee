import serial
import time
import OSC
from xbee import XBee


#OSC
send_addr = '192.168.0.2', 57120
c = OSC.OSCClient()
c.connect(send_addr)

oscmsg = OSC.OSCMessage()
oscmsg.setAddress("/xbee")

serial_port = serial.Serial('/dev/ttyAMA0', 57600)
xbee = XBee(serial_port)

# OSC send enable : 1
osc = 1

while True:
    try:


        #TX - Temporary
        #'bn' is - b: from 'b', n: not to CENTER just to 'a'.
        xbee.tx(dest_addr='\xff\xff', data='bn')
        #time.sleep(0.01) #wait 0.001 sec
 

        #RX
        get = xbee.wait_read_frame()
        #print(get)
        data = get['rf_data'][0]
        print("data: ", data)
        fwdedrssi = ord(get['rf_data'][1])
        print("rssi: ", fwdedrssi)
        
        if data == '\xab':
            #send OSC to PureData (data, rssi)
            oscmsg.setAddress("/dist_AB")
            print("send OSC to A-B\n")
        elif data == '\xbc':
            oscmsg.setAddress("/dist_BC")
            print("send OSC to B-C\n")
        elif data == '\xca':
            oscmsg.setAddress("/dist_CA")
            print("send OSC to C-A\n")
        else:
            fwdedrssi = 0
            oscmsg.setAddress("/nowhere")
            #print("data: ", data)
            print("Wrong distance category.\n")
        
        #append distance category and rssi of it.
        #oscmsg.append(data)
        oscmsg.append(fwdedrssi)

        #send and clear
        if osc == 1 and fwdedrssi != 0:
            c.send(oscmsg)
            oscmsg.clearData()
                
    except KeyboardInterrupt:
        break

#serial port close
serial_port.close()
#osc client close
c.close()


