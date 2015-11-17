import serial
import time
import OSC
from xbee import XBee,ZigBee


#OSC
send_addr = 'localhost', 5557
#send_addr = '192.168.0.2', 5555
c = OSC.OSCClient()
c.connect(send_addr)
oscmsg = OSC.OSCMessage()

serial_port = serial.Serial('/dev/ttyAMA0', 57600)
xbee = XBee(serial_port, escaped=True)

# DEFINE
RX_TIME_LIMIT = 100
DELAY_NUM_LIMIT = 3 

# OSC send enable : 1
oscSendEnable = 1
nodeNum = 3
dest_addrs = ['\x0a\x0a', '\x1b\x1b', '\x2c\x2c']
dest_IDs = ['A', 'B', 'C']
nodeStatus = [1, 1, 1]
#nodeStatusConst = [1, 1, 1]

updateTime = [0, 0, 0] 
timeInterval = 0
isNetworkStart = 0 #0 default
curMilliTime = lambda: int(round(time.time() * 1000))
delayNum = 0
soloSendTime = 0
lastMsgFrom = 0

count = 0

# Functions
def dataProcess(data) :
    moduleAlone = False
    global isNetworkStart
    isNetworkStart = 1

    fwRSSI = [0, 0, 0]
    rssi = [0, 0, 0]
    idStr = ["3->1", "1->2", "2->3"]

    distID = ord(data['rf_data'][0])
    fwRSSI[distID-1] = ord(data['rf_data'][1])
    rssi[distID-1] = ord(data['rssi'][0])

    if fwRSSI[distID-1] == ord('s'):
        soloSendTime = 0
#        print data
        moduleAlone = True
        #Make CenterModule respond.
#        print "Msg von allein module kam.\n"
        time.sleep(0.001)
        xbee.tx(dest_addr=dest_addrs[distID-1], data='y')
        soloSendTime = curMilliTime()

    elif fwRSSI[distID-1] == ord('R'):
        print data
        # Module distID-1 reseted. Let join it into networing agagin.
        if nodeNum == 2:
            print "Reset 2 -> 3\n"
            xbee.tx(dest_addr=dest_addrs[((distID-1)+2)%3], data='j')
        elif nodeNum == 1:
            aliveNodeNum = 0
            print "nodeStatus"
            print nodeStatus
            for i in range(0, 3):
                if nodeStatus[i] == 1:
                    aliveNodeNum = i
                    print "aliveNode : %d" % aliveNodeNum
                    continue
            dataSum = 'K' + str(distID)
            print "dataSum : %s" % dataSum 
            print "Reset 1 -> 2\n"
            xbee.tx(dest_addr=dest_addrs[aliveNodeNum], data=dataSum)

                

    global lastMsgFrom
    lastMsgFrom = distID - 1 # 0, 1, 2
#    print "lastMsgFrom: %d" % lastMsgFrom
   
    if moduleAlone is False:
        updateTime[distID-1] = curMilliTime()

        #Between moduel and another module
        #send OSC to PureData (data, rssi)
        oscmsg.setAddress("/dist")
        oscmsg.append(distID-1)
        oscmsg.append(fwRSSI[distID-1])

        if oscSendEnable :
            c.send(oscmsg)

        oscmsg.clearData()

    #Between module and CenterModule
    oscmsg.setAddress("/rssi")
    oscmsg.append(distID-1)
    oscmsg.append(rssi[distID-1])

    if oscSendEnable :
        c.send(oscmsg)

    oscmsg.clearData()

#    if distID == 1:
#        print("DistanceID: %s / forwarded RSSI: %d" %(idStr[distID-1], fwRSSI[distID-1]))
#        print("RSSI between CENTER and MODULE %d : %d" %(distID, rssi[distID-1]))


    # Check node status / Number
    if fwRSSI[distID-1] != ord('R'):
        nodeStatus[distID - 1] = 1
    
    global nodeNum

    nodeNumTmp = 0
    for i in nodeStatus:
        nodeNumTmp = nodeNumTmp + i

    nodeNum = max(nodeNum, nodeNumTmp)
#    print "nodeNum : %d" % nodeNum

    if nodeNum > 1:
        moduleAlone = False
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
        nodeStatus = [0, 0, 0]
        timeInterval = timeInterval + 1
        time.sleep(0.5)
#        print timeInterval

        if isNetworkStart :

            #Re send to solo module
            if nodeNum == 1 and curMilliTime() - soloSendTime > RX_TIME_LIMIT:
                xbee.tx(dest_addr=dest_addrs[lastMsgFrom], data='y')
                soloSendTime = curMilliTime()
                print "Resend solo\n"

            for i in range(0, 3):
#                print i
                delay = curMilliTime() - updateTime[i]
#                print ("%s, delay %d" % (dest_IDs[i], delay) )
                if delay > RX_TIME_LIMIT and i == lastMsgFrom and nodeNum >= 2:

#                    print "Network is delaying.\n"
#                    print ("Delayed time of %s : %d\n" % (dest_IDs[i], delay))

                    # Send recovery signal to Next module.
                    # Pseudo msg
                    payload = dest_IDs[i]
                    
                    if nodeNum == 2:
                        if i == aliveNodeA:
                            xbee.tx(dest_addr=dest_addrs[aliveNodeB], data=payload)
                            print ("NodeNum: 2, Pseudo msg sent %s -> %s" %(dest_IDs[aliveNodeA], dest_IDs[aliveNodeB]) )
                        elif i == aliveNodeB:
                            xbee.tx(dest_addr=dest_addrs[aliveNodeA], data=payload)
                            print ("NodeNum: 2, Pseudo msg sent %s -> %s" %(dest_IDs[aliveNodeB], dest_IDs[aliveNodeA]) )

                    elif nodeNum == 3:
                        print ("NodeNum: 3, Pseudo msg sent %s -> %s" %(dest_IDs[i], dest_IDs[(i+1)%3]) )
                        xbee.tx(dest_addr=dest_addrs[(i+1)%3], data=payload)

                    for j in range(0, 3):
                        updateTime[j] = curMilliTime()

                    global delayNum
                    delayNum = delayNum + 1
                    print ("delayNum: %d" % delayNum)

                    if delayNum > DELAY_NUM_LIMIT:
                        print ("Can not find module %s, so ignore it." % (dest_IDs[(i+1)%3]) )

                        if nodeNum == 2:
                            # Ignoring
                            print "Case nodeNum == 1\n"
                            print "i: %d\n" % i
                            xbee.tx(dest_addr=dest_addrs[i], data='S')
                            nodeStatus = [0, 0, 0]
                            nodeStatus[i] = 1
                            delayNum = 0
                            nodeNum = nodeNum - 1

                            # Clear dead module's osc msg.
                            oscmsg.setAddress("/dist")
                            if i == aliveNodeA:
                                oscmsg.append(aliveNodeB)
                            elif i == aliveNodeB:
                                oscmsg.append(aliveNodeA)
                            oscmsg.append(0)
                            if oscSendEnable :
                                c.send(oscmsg)
                            oscmsg.clearData()

                            oscmsg.setAddress("/rssi")
                            if i == aliveNodeA:
                                oscmsg.append(aliveNodeB)
                            elif i == aliveNodeB:
                                oscmsg.append(aliveNodeA)
                            oscmsg.append(0)
                            if oscSendEnable :
                                c.send(oscmsg)
                            oscmsg.clearData()


                        if nodeNum == 3:
                            # Ignoring
                            print "Case nodeNum == 2\n"
                            xbee.tx(dest_addr=dest_addrs[(i+2)%3], data='I')
                            nodeStatus[(i+1)%3] = 0
                            global aliveNodeA
                            aliveNodeA = i
                            global aliveNodeB
                            aliveNodeB = (i+2)%3
                            delayNum = 0
                            nodeNum = nodeNum - 1

                            # Clear dead module's osc msg.
                            oscmsg.setAddress("/dist")
                            oscmsg.append(i+1)
                            oscmsg.append(0)
                            if oscSendEnable :
                                c.send(oscmsg)
                            oscmsg.clearData()

                            oscmsg.setAddress("/rssi")
                            oscmsg.append(i+1)
                            oscmsg.append(0)
                            if oscSendEnable :
                                c.send(oscmsg)
                            oscmsg.clearData()


    except KeyboardInterrupt:
        break


#close
xbee.halt()
serial_port.close()
c.close()
