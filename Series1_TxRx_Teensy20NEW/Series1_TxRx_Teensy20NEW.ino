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
0 : 1st module (0x0A0A)
1 : 2nd module (0x1B1B)
2 : 3rd module (0x2C2C)
3 : CENTER MODULE (0x3D3D)
*/
#define PREV_MODULE 2 // Set previous module number
#define MODULE_NUM 0 // Set this module number
#define NEXT_MODULE 1 // Set next module number


#define DEBUG
#define RSPTIME 100
#define STARTUP_DELAY 1000

uint8_t senderID[] = {'A', 'B', 'C', 'D'}; // 'D' is Center module.
uint8_t distID[] = {1, 2, 3};
uint16_t addr_dest[]= {0x0A0A, 0x1B1B, 0x2C2C, 0x3D3D};

XBee xbee = XBee();
HardwareSerial Uart = HardwareSerial(); // For Teensy 2.0 only.


// TX
uint8_t payload[] = { senderID[MODULE_NUM] };
uint8_t payloadToC[] = { senderID[MODULE_NUM], 0 };

Tx16Request tx = Tx16Request(addr_dest[NEXT_MODULE], payload, sizeof(payload)); // to next module
Tx16Request txC = Tx16Request(addr_dest[3], payloadToC, sizeof(payloadToC)); // to center module


// RX
XBeeResponse response = XBeeResponse();
// create reusable response objects for responses we expect to handle 
Rx16Response rx16 = Rx16Response();

// IO pins for Teensy 2.0
int txLed = 11; // 13 for Teensy 3.0
int rxLed = 12; // 16 for Teensy 3.0
int but = 0;


// Variables
uint8_t getSenderID = 0;
uint8_t rssi = 0;
unsigned long nextTime = 0;
boolean reachedGood = false;


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
      if (!digitalRead(but)){
        xbee.send(tx);
      }
      
      
      // Receive from previous module      
      xbee.readPacket();
      
        if (xbee.getResponse().isAvailable()) {
          Serial.println("Waiting...");                
          Serial.println("--------------------Available");
          getSenderID = 0;
          rssi = 0;
          reachedGood = false;
//
//#ifdef DEBUG
//              Serial.print("reachedGood: ");
//              Serial.println(reachedGood);
//              
//              Serial.print("getSenderID: ");
//              Serial.println(getSenderID);
//
//              Serial.print("rssi: ");
//              Serial.println(rssi);
//              
//#endif
//
//          
//          
            if (xbee.getResponse().getApiId() == RX_16_RESPONSE) {

#ifdef DEBUG
            // got something
              Serial.println("--------------------Coming");            
              Serial.println("Serial datas are comming.");            
#endif

            // got a rx packet
              flashLed(rxLed, 1, 10);                  
              xbee.getResponse().getRx16Response(rx16);
              getSenderID = rx16.getData(0);
              rssi = rx16.getRssi();
//              inRead = false;
              

#ifdef DEBUG
            Serial.print("senderID: "); Serial.println(char(getSenderID)); //received as Decimal Number
            Serial.print("RSSI: "); Serial.println(rssi);
       
#endif
            }else if(xbee.getResponse().isError()) {
              Serial.println("Error reading packet.  Error code: ");  
              Serial.println(xbee.getResponse().getErrorCode());
              // Do something to resolve error.
            }
            
        }

// Send to Center module

//        if (inRead == false){
          if (getSenderID != 0 && getSenderID == senderID[PREV_MODULE]){
              
              // Receive msg from previous module 
              // Send to CENTER module.
              payloadToC[0] = distID[MODULE_NUM]; // one of 1, 2, 3
              payloadToC[1] = rssi;
              xbee.send(txC);
              flashLed(txLed, 1, 10);
              
              // Send another Module to give rssi.
              payload[0] = senderID[MODULE_NUM]; // one of 'A', 'B', 'C'
              xbee.send(tx);
//              flashLed(txLed, 1, 10);
              reachedGood = false; // Exactly, unknown yet.
                
              while(!reachedGood) {
                
                if (xbee.readPacket(RSPTIME)) {
                TxStatusResponse txStatus = TxStatusResponse();          
    
                if (xbee.getResponse().getApiId() == TX_STATUS_RESPONSE) {
                  xbee.getResponse().getZBTxStatusResponse(txStatus);
    
                  if (txStatus.getStatus() == SUCCESS) {
                     // another msg sendable
#ifdef DEBUG
            Serial.println("--------------------Success ending");            
            Serial.print("Reached Good Confirmed to ");
            Serial.println(NEXT_MODULE);
            Serial.print("CYCLE END\n");             
            Serial.print("\n");             
#endif                     
                     flashLed(txLed, 1, 10);
                     reachedGood = true;
                     break;
                  }else{
                    // get response but it is not SUCCESS
                    xbee.send(tx);
                    reachedGood = false;
                    continue;
                  }
                }else{
                  xbee.send(tx);
                  reachedGood = false;
                  continue;
                }
              }else{
                Serial.println("In else of while loop.");
                //Didn't readPacket at all after RSPTIME.
                // Send again
                xbee.send(tx);
//                flashLed(txLed, 1, 10);
                reachedGood = false;
                continue;
              }
            }
            
            
            
            
          }
          
        }
      }
