n = NetAddr("192.168.0.20", 5558); // Send to RPI
n.sendMsg("/recReq", 1);
n.sendMsg("/recReq", 0);
