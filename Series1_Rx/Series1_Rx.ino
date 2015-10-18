/**
 * Copyright (c) 2009 Andrew Rapp. All rights reserved.
 *
 * This file is part of XBee-Arduino.
 *
 * XBee-Arduino is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * XBee-Arduino is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with XBee-Arduino.  If not, see <http://www.gnu.org/licenses/>.
 */

#include <XBee.h>

/*
This example is for Series 1 XBee (802.15.4)
Receives either a RX16 or RX64 packet and sets a PWM value based on packet data.
Error led is flashed if an unexpected packet is received
*/

#define DEBUG

#define ID 'a'
#define SENDER_ID 'b'
#define STARTUP_DELAY 15000
#define NOT_TO_CENTER 'n'
//#define NOT_TO_CENTER 'b'
#define RSSI_DIR 0xab


XBee xbee = XBee();

//TX
uint8_t payload[] = { ID, 0 }; //ID / to Center or Not
XBeeAddress64 addr64 = XBeeAddress64(0x00000000, 0x0000ffff); //Broadcast addr
Tx64Request tx = Tx64Request(addr64, payload, sizeof(payload));


//RX
XBeeResponse response = XBeeResponse();
// create reusable response objects for responses we expect to handle 
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response();


int statusLed = 13;
int errorLed = 2;
//int dataLed = 10;

uint8_t option = 0;
uint8_t senderID = 0;
uint8_t toc = 0;
uint8_t rssi = 0;

unsigned long nextTime = 0;

void flashLed(int pin, int times, int wait) {
    for (int i = 0; i < times; i++) {
        digitalWrite(pin, HIGH);
        delay(wait);
        digitalWrite(pin, LOW);
      
        if (i + 1 < times) {
            delay(wait);
        }
    }
}

void setup() {
    pinMode(statusLed, OUTPUT);
    pinMode(errorLed, OUTPUT);
//  pinMode(dataLed,  OUTPUT);
  
    Serial.begin(9600); //start USB serial
  
  
    // start serial1 for xbee UART serial
    Serial1.begin(57600);
    xbee.setSerial(Serial1);
  
    flashLed(statusLed, 3, 50);

}

// continuously reads packets, looking for RX16 or RX64
void loop() {
    delay(STARTUP_DELAY);

    while(1){
        //TX

        //Broad cast with ID
        payload[0] = ID;
        payload[1] = NOT_TO_CENTER;
      
        xbee.send(tx);

        // flash TX indicator
        flashLed(statusLed, 1, 10);

        //RX : read packet from everywhere 

        xbee.readPacket();
    
        if (xbee.getResponse().isAvailable()) {
          
            if (xbee.getResponse().getApiId() == RX_16_RESPONSE || xbee.getResponse().getApiId() == RX_64_RESPONSE) {

#ifdef DEBUG
            // got something
            Serial.println("Serial comming");
#endif
            
                // got a rx packet
                if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {
                    xbee.getResponse().getRx16Response(rx16);
                    senderID = rx16.getData(0);
                    rssi = rx16.getRssi();
                    //option = rx16.getOption();
                    //toc = rx16.getData(1);
            } else {
                    xbee.getResponse().getRx64Response(rx64);
                    senderID = rx64.getData(0);
                    rssi = rx64.getRssi();        
                    //option = rx64.getOption();
                    //toc = rx16.getData(1);        
            }


#ifdef DEBUG
            Serial.print("senderID: "); Serial.println(senderID); //received as Decimal Number
            Serial.print("RSSI: "); Serial.println(rssi);
            Serial.print("\n");        
#endif

                
            // need to get data from ID 'b' only
            if (senderID == SENDER_ID) {
#ifdef DEBUG              
                Serial.print("Matching sender ID arrived.");
#endif              
                // forward to the RSSI to CENTER
                // payload[0] 
                // 0xab : a received, b sent rssi. 
                // 0xbc : b received, c sent rssi. 
                // 0xca : c received, a sent rssi. 
                payload[0] = RSSI_DIR;
                payload[1] = rssi;
          
                xbee.send(tx);
                Serial.print("sending to Center finished.\n");
                

                // flash TX indicator
                flashLed(statusLed, 1, 10);
            }
            
            flashLed(statusLed, 1, 10);
          
            } else {
              // something wrong packet
              flashLed(errorLed, 1, 25);    
            }
      } else if(xbee.getResponse().isError()) {
          //nss.print("Error reading packet.  Error code: ");  
          //nss.println(xbee.getResponse().getErrorCode());
          // or flash error led
      }
    }
}
