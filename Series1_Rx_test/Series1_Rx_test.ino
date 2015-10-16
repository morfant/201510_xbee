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
#define ID 1

XBee xbee = XBee();

//TX
uint8_t payload[] = { ID, 0 }; //ID / to Center or Not
Tx16Request tx = Tx16Request(0x1, payload, sizeof(payload));


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
    
  
    xbee.readPacket();
    
    if (xbee.getResponse().isAvailable()) {
      Serial.println("Serial comming");
      // got something
      
      if (xbee.getResponse().getApiId() == RX_16_RESPONSE || xbee.getResponse().getApiId() == RX_64_RESPONSE) {
        // got a rx packet
        
        if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {
                xbee.getResponse().getRx16Response(rx16);
        	option = rx16.getOption();
        	senderID = rx16.getData(0);
                toc = rx16.getData(1);
                rssi = rx16.getRssi();
        } else {
                xbee.getResponse().getRx64Response(rx64);
        	option = rx64.getOption();
        	senderID = rx64.getData(0);
                toc = rx16.getData(1);        
                rssi = rx64.getRssi();        
        }
        
        Serial.print("senderID: "); Serial.println(senderID); //received as Decimal Number
        Serial.print("is to C: "); Serial.println(toc);
        Serial.print("RSSI: "); Serial.println(rssi);
        Serial.print("\n");        
        
        // TODO check option, rssi bytes    
        flashLed(statusLed, 1, 10);
        
        // broad cast RSSI to Center /w ID
        
        
        // braodcast ID(/w rssi)

      } else {
      	// not something we were expecting
        flashLed(errorLed, 1, 25);    
      }
    } else if (xbee.getResponse().isError()) {
      //nss.print("Error reading packet.  Error code: ");  
      //nss.println(xbee.getResponse().getErrorCode());
      // or flash error led
    }

   /*   
   //TX      
   // start transmitting after a startup delay.  Note: this will rollover to 0 eventually so not best way to handle
    if (millis() - nextTime > 1000) {
      payload[0] = ID;
      payload[1] = 'c';
      // break down 10-bit reading into two bytes and place in payload
      
      xbee.send(tx);

      // flash TX indicator
      flashLed(statusLed, 1, 100);
      
      nextTime = millis();
      
    }
    
    */
    
}
