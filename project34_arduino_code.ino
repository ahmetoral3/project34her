#include <SPI.h>
#include <Stepper.h>
#include "Adafruit_Thermal.h"
#include "SoftwareSerial.h"
#include <Wire.h>

#define RST_PIN         5           // Configurable, see typical pin layout above
#define SS_PIN          53          // Configurable, see typical pin layout above
#define TX_PIN 22 // Arduino transmit  YELLOW WIRE  labeled RX on printer
#define RX_PIN 24 // Arduino receive   GREEN WIRE   labeled TX on printer

SoftwareSerial mySerial(RX_PIN, TX_PIN); // Declare SoftwareSerial obj first
Adafruit_Thermal printer(&mySerial); 


const int stepsPerRevolution = 2038;
Stepper stepper5 = Stepper(stepsPerRevolution, 10, 12, 11, 13);
Stepper stepper10 = Stepper(stepsPerRevolution, 6, 8, 7, 9);
Stepper stepper20 = Stepper(stepsPerRevolution, 2, 4, 3, 5);
int dat = 0;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    String data = Serial.readStringUntil('\n');
    if (data.indexOf('$') >= 0){
      data.remove(0,1);
      dat = data.toInt();
      while(dat != 0){
        stepper5.setSpeed(10);
        stepper5.step(stepsPerRevolution);
        dat--;
      }
    }else if(data.indexOf('%') >= 0){
      data.remove(0,1);
      dat = data.toInt();
      while(dat != 0){
        stepper10.setSpeed(10);
        stepper10.step(stepsPerRevolution);
        dat--;
      }
    }else if(data.indexOf('!') >= 0){
      data.remove(0,1);
      dat = data.toInt();
      while(dat != 0){
        stepper20.setSpeed(10);
        stepper20.step(stepsPerRevolution);
        dat--;
      }
    }else  if (data.indexOf('&') >= 0){
      data.remove(0,1);
      String temp = data;
      temp.remove(0,18);
      String iban = data;
      iban.remove(18,30);
  pinMode(26, OUTPUT); 
  digitalWrite(26, LOW);
  mySerial.begin(9600);  // Initialize SoftwareSerial
  printer.begin();        // Init printer (same regardless of serial type)

 
  printer.justify('C');
  printer.setSize('L');
  printer.boldOn();
  printer.println(F("E.X.I.T. BANK"));
  printer.boldOff();
  printer.setSize('S');
  printer.justify('L');

  printer.justify('L');
  printer.inverseOn();
  printer.println(F("Amount withdrawn:               "));
  printer.inverseOff();
  printer.justify('R');
  printer.setSize('L');
  printer.println(temp+",- Pounds");
  printer.setSize('S');
  printer.justify('L');

  printer.inverseOn();
  printer.println(F("Info:                           "));
  printer.inverseOff();
  
  printer.boldOn();
  printer.println(F("Account number:"));
  printer.boldOff();
  printer.justify('R');
  printer.println("**** **"+iban);
  printer.justify('L');

  printer.boldOn();
  printer.println(F("Location:"));
  printer.boldOff();
  printer.justify('R');
  printer.println("EXIT");
  printer.justify('L');

  printer.feed(2); 
  
  printer.inverseOn();
  printer.justify('C');
  printer.setSize('L');
  printer.println(F("   THANK YOU   "));
  printer.setSize('S');
  printer.inverseOff();
  printer.println(F("www.exit.com"));
  
  printer.feed(2);

  printer.sleep();      // Tell printer to sleep
  delay(3000);          // Sleep for 3 seconds
  printer.wake();       // MUST wake() before printing again, even if reset
  printer.setDefault(); // Restore printer to defaults
    
  }
  }
}
