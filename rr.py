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

# DEFINE
RX_TIME_LIMIT = 100
DELAY_NUM_LIMIT = 10

# OSC send enable : 1
oscSendEnable = 0
dest_addrs = ['\x0a\x0a', '\x1b\x1b', '\x2c\x2c']
dest_IDs = ['A', 'B', 'C']
nodeStatus = [1, 1, 1]

updateTime = [0, 0, 0] 
timeInterval = 0
isNetworkStart = 0 #0 default
curMilliTime = lambda: int(round(time.time() * 1000))
delayNum = 0

lastMsgFrom = 0

count = 0

# Functions
def dataProcess(data) :
    global isNetworkStart
    isNetworkStart = 1

    fwRSSI = [0, 0, 0]
    rssi = [0, 0, 0]
    idStr = ["3->1", "1->2", "2->3"]

    distID = ord(data['rf_data'][0])
    fwRSSI[distID-1] = ord(data['rf_data'][1])
    rssi[distID-1] = ord(data['rssi'][0])


    if fwRSSI[distID-1] == ord('R'):
        print data
        print "Reset"
        # Module distID-1 reseted. Let join it into networing agagin.
        for i in range(0, 10):
            xbee.tx(dest_addr=dest_addrs[((distID-1)+2)%3], data='j')


    global lastMsgFrom
    lastMsgFrom = distID - 1 # 0, 1, 2
#    print "lastMsgFrom: %d" % lastMsgFrom
    
    updateTime[distID-1] = curMilliTime()
    


    #send OSC to PureData (data, rssi)
    oscmsg.setAddress("/dist_" + idStr[distID-1])
    oscmsg.append(fwRSSI[distID-1])
    oscmsg.append(rssi[distID-1])

    if oscSendEnable :
        c.send(oscmsg)

    oscmsg.clearData()

#    if distID == 1:
#        print("DistanceID: %s / forwarded RSSI: %d" %(idStr[distID-1], fwRSSI[distID-1]))
#        print("RSSI between CENTER and MODULE %d : %d" %(distID, rssi[distID-1]))


    # Reset delayNum count
    global delayNum
    delayNum = 0

# Set xbee asynchronosly
xbee = XBee(serial_port, callback=dataProcess)

def checkNode() :
    for i in dest_addrs:
        xbee.tx(dest_addr=i, data='N')


def getDeActNode() :
    for k in range(0, 3):
        if nodeStatus[k] == 0:
            deActiveNode = k
            continue
    return deActiveNode

   
# Main loop
while True:
    try:
        timeInterval = timeInterval + 1
        time.sleep(0.5)
#        print timeInterval

        if isNetworkStart :
            for i in range(0, 3):
#                print i
                delay = curMilliTime() - updateTime[i]
#                print ("%s, delay %d" % (dest_IDs[i], delay) )
                if delay > RX_TIME_LIMIT and i == lastMsgFrom:

#                    print "Network is delaying.\n"
#                    print ("Delayed time of %s : %d\n" % (dest_IDs[i], delay))

                    # Send recovery signal to Next module.
                    # Pseudo msg
                    payload = dest_IDs[i]
                    print ("Pseudo msg sent %s -> %s" %(dest_IDs[i], dest_IDs[(i+1)%3]) )

                    xbee.tx(dest_addr=dest_addrs[(i+1)%3], data=payload)

                    for j in range(0, 3):
                        updateTime[j] = curMilliTime()

                    global delayNum
                    delayNum = delayNum + 1
                    print ("delayNum: %d" % delayNum)

                    if delayNum > DELAY_NUM_LIMIT:
                        print ("Can not find module %s, so ignore it." % (dest_IDs[(i+1)%3]) )

                        # Ignoring
                        xbee.tx(dest_addr=dest_addrs[(i+2)%3], data='I')
                        delayNum = 0

    except KeyboardInterrupt:
        break


#close
xbee.halt()
serial_port.close()
c.close()




