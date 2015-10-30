import serial
import time
import OSC
from xbee import XBee


#OSC
send_addr = 'localhost', 5555
c = OSC.OSCClient()
c.connect(send_addr)
oscmsg = OSC.OSCMessage()

serial_port = serial.Serial('/dev/ttyAMA0', 57600)
xbee = XBee(serial_port)

# OSC send enable : 1
oscSendEnable = 1

while True:
    try:


        #TX - Temporary
#        xbee.tx(dest_addr='\xff\xff', data='bn')
 

        #RX
        get = xbee.wait_read_frame()


        fwRSSI = list()
        rssi = list()
        idStr = ["3-1", "1-2", "2-3"]

        distID = ord(get['rf_data'][0])
        rssiChk = ord(get['rf_data'][1])

        if rssiChk == 0 :
            print(get)
            print("DistanceID: ", idStr[distID-1], "/ forwarded RSSI: ", rssiChk)
            print("RSSI: ", ord(get['rssi'][0]))
            continue


        fwRSSI[distID-1] = ord(get['rf_data'][1])
        rssi[distID-1] = ord(get['rssi'][0])

        #send OSC to PureData (data, rssi)
        oscmsg.setAddress("/dist_" + idStr[distID-1])
        oscmsg.append(fwRSSI[distID-1])
        oscmsg.append(rssi[distID-1])

        if oscSendEnable :
            c.send(oscmsg)

        oscmsg.clearData()

        print("DistanceID: ", idStr[distID-1], "/ forwarded RSSI: ", fwRSSI[distID-1])
        print("RSSI: ", rssi[distID-1])

       
    except KeyboardInterrupt:
        break

#serial port close
serial_port.close()
#osc client close
c.close()


