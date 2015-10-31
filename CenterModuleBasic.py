import serial
import time
import OSC
from xbee import XBee,ZigBee


#OSC
send_addr = 'localhost', 5555
c = OSC.OSCClient()
c.connect(send_addr)
oscmsg = OSC.OSCMessage()

serial_port = serial.Serial('/dev/ttyAMA0', 57600)
xbee = XBee(serial_port)

# OSC send enable : 1
oscSendEnable = 0
dest_addrs = ['\x0a\x0a', '\x1b\x1b', '\x2c\x2c']
nodeAlive = [1, 1, 1]# 1 is alive, 0 is unknown, -1 is dead
updateTime = 5 
timeInterval = 0
isNetworkStart = 1 #0 default
netCheckMode = 0 
curMilliTime = lambda: int(round(time.time() * 1000))

def dataProcess(data) :
    if netCheckMode == 1:
        print data
    global isNetworkStart
    isNetworkStart = 1
    global timeInterval
    timeInterval = 0

    fwRSSI = [0, 0, 0]
    rssi = [0, 0, 0]
    idStr = ["3->1", "1->2", "2->3"]

    distID = ord(data['rf_data'][0])
    fwRSSI[distID-1] = ord(data['rf_data'][1])
    rssi[distID-1] = ord(data['rssi'][0])

    #node alive checker
    if fwRSSI[distID-1] == 120: #'x'
        nodeAlive[distID-1] = 1
        print("Node %d is alive!" % distID)
    else :
        nodeAlive[distID-1] = 0

    


    #send OSC to PureData (data, rssi)
    oscmsg.setAddress("/dist_" + idStr[distID-1])
    oscmsg.append(fwRSSI[distID-1])
    oscmsg.append(rssi[distID-1])

    if oscSendEnable :
        c.send(oscmsg)

    oscmsg.clearData()

    if distID == 1:
        print("DistanceID: %s / forwarded RSSI: %d" %(idStr[distID-1], fwRSSI[distID-1]))
        print("RSSI between CENTER and MODULE %d : %d" %(distID, rssi[distID-1]))


xbee = XBee(serial_port, callback=dataProcess)

def checkNode() :
    for i in dest_addrs:
        xbee.tx(dest_addr=i, data='N')

while True:
    try:
        timeInterval = timeInterval + 1
        time.sleep(0.1)
#        print timeInterval

        if isNetworkStart :
            if timeInterval > updateTime :
                print "Networking broken."
                checkNode()
                netCheckMode = 1
                #Fix it
#                isNetworkStart = 0

    except KeyboardInterrupt:
        break


#close
xbee.halt()
serial_port.close()
c.close()




