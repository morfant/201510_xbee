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
#define MODULE_NUM 1 // Set module number (0, 1, 2)

#define DEBUG
#define RSPTIME 100
#define STARTUP_DELAY 15000

uint8_t senderID[] = {'A', 'B', 'C'};
uint8_t distID[] = {1, 2, 3};
uint16_t addr_dest[]= {0x0A0A, 0x1B1B, 0x2C2C, 0x3D3D};

XBee xbee = XBee();
HardwareSerial Uart = HardwareSerial(); // For Teensy 2.0 only.


// TX
uint8_t payload[] = { senderID[MODULE_NUM] };
uint8_t payloadToC[] = { senderID[MODULE_NUM], 0 };

Tx16Request tx = Tx16Request(addr_dest[(MODULE_NUM+1)%3], payload, sizeof(payload)); // to next module
Tx16Request txC = Tx16Request(addr_dest[3], payloadToC, sizeof(payloadToC)); // to center module


// RX
XBeeResponse response = XBeeResponse();
// create reusable response objects for responses we expect to handle 
Rx16Response rx16 = Rx16Response();
Rx64Response rx64 = Rx64Response(); // Is it Needed?

// IO pins for Teensy 2.0
int txLed = 11;
int rxLed = 12;
int but = 0;


// Variables
uint8_t getSenderID = 0;
uint8_t rssi = 0;
unsigned long nextTime = 0;
boolean inRead = true;
boolean sendable = true;


// Functions
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


// Setup
void setup() {
    pinMode(txLed, OUTPUT);
    pinMode(rxLed, OUTPUT);
    pinMode(but, INPUT_PULLUP);
  
    //start USB serial  
    Serial.begin(9600);
  
  
    // start serial1 for xbee UART serial
//    Uart.begin(57600); // Not working
    Uart.begin(58824); // Working with xbee(57600)
    xbee.setSerial(Uart);
  
    // Start signal
    flashLed(txLed, 1, 50);
    flashLed(rxLed, 1, 50);    
    flashLed(txLed, 1, 50);    
}



// continuously reads packets, looking for RX16 or RX64
void loop() {
    delay(STARTUP_DELAY); // Is it needed?

    while(1){
      
      // Receive from previous module
      
      xbee.readPacket();
      
      
      
      
        if (xbee.getResponse().isAvailable()) {
      Serial.println("Waiting...");      
            inRead = true;
            if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {

#ifdef DEBUG
            // got something
              Serial.println("Serial datas are comming.");            
#endif
              getSenderID = 0;
              rssi = 0;

            // got a rx packet
              flashLed(rxLed, 1, 10);                  
              xbee.getResponse().getRx16Response(rx16);
              getSenderID = rx16.getData(0);
              rssi = rx16.getRssi();
              inRead = false;

#ifdef DEBUG
            Serial.print("senderID: "); Serial.println(getSenderID); //received as Decimal Number
            Serial.print("RSSI: "); Serial.println(rssi);
            Serial.print("\n");        
#endif
            }else if(xbee.getResponse().isError()) {
              Serial.println("Error reading packet.  Error code: ");  
              Serial.println(xbee.getResponse().getErrorCode());
            }
            
        }

// Send to Center module

        if (inRead == false){
          if (getSenderID == senderID[(MODULE_NUM+2)%3]){
              // Receive msg from previous module.
              payloadToC[0] = distID[MODULE_NUM];
              payloadToC[1] = rssi;
              
          }else{
              // Didn't receive msg from previous module.
              payloadToC[0] = distID[MODULE_NUM];
              payloadToC[1] = 0;
          }
      
         // Buttom push check 
         if(!digitalRead(but)){
             // Do something special.
          }
  
          xbee.send(txC);
          flashLed(txLed, 1, 10);
  
  
  // Send to next module
          payload[0] = senderID[MODULE_NUM];
          xbee.send(tx);
          flashLed(txLed, 1, 10);
        }
      }
      
      
      
// after sending a tx request, we expect a status response
// wait up to 5 seconds for the status response

        if (xbee.readPacket(RSPTIME)) {
          TxStatusResponse txStatus = TxStatusResponse();          
        // got a response!
        // should be a znet tx status 
          if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
            xbee.getResponse().getZBTxStatusResponse(txStatus);
            // get the delivery status, the fifth byte
            if (txStatus.getStatus() == SUCCESS) {
               // another msg sendable
               flashLed(rxLed, 1, 10);
               sendable = true;
            }
          }  
        }else{
          sendable = true;          
        }
      
}
