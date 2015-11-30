n = NetAddr("192.168.1.77", 5558); // Send to RPI at jjwc2
n = NetAddr("192.168.1.108", 5558); // Send to RPI at EGG
n = NetAddr("localhost", 5558); // Send to RPI at local

n.sendMsg("/recCtrl", 1); //Rec start
n.sendMsg("/recCtrl", 0); //Rec stop

n.sendMsg("/metroCtrl", 1); //metronome On
n.sendMsg("/metroCtrl", 0); //metronome Off
n.sendMsg("/metroCtrl", 1200); //metronome speed setup. 1000 = 1sec.

n.sendMsg("/bcsoundCtrl", 1); //Between Center sound On
n.sendMsg("/bcsoundCtrl", 0); //Between Center sound Off
