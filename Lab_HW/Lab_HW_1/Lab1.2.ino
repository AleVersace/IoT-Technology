//Lab1.2 - Read the status of two leds using the serial monitor
#include <TimerOne.h>

//Define leds pins
const int RLED_PIN = 12;
const int GLED_PIN = 11;

//Define leds half periods
const float R_HALF_PERIOD = 1.5;
const float G_HALF_PERIOD = 3.5;

//Set initial state of the leds as LOW. They are volatile because are used by both the ISR and by the loop
volatile int greenLedState = LOW;
volatile int redLedState = LOW;

//ISR function
void blinkGreen() {
  greenLedState = !greenLedState;
  digitalWrite(GLED_PIN, greenLedState);
}

//Read from the serial port
void serialPrintStatus() {
  //Read bytes only if there is something in the buffer
  if (Serial.available() > 0) {
    //Read 1 byte from the buffer
    int inByte = Serial.read();
    //If the read byte corresponds to the ASCII code of 'r'
    if (inByte == 114) {
      Serial.println("The red led has status: " + String(redLedState));
    }
    //If the read byte corresponds to the ASCII code of 'g'
    else if (inByte == 103) {
      Serial.println("The green led has status: " + String(greenLedState));
    }
    //If the ASCII doesn't correspond to 'r' or 'g' return error
    else {
      Serial.println("Error - command not valid [r=red, g=green]");
    }
  }
}


void setup() {
  Serial.begin(9600);     //Initialize serial comunication
  while (!Serial);      //Loop won't start untill the serial monitor is open
  Serial.println("Lab 1.2 Starting");     //Welcome message
  pinMode(RLED_PIN, OUTPUT);
  pinMode(GLED_PIN, OUTPUT);
  Timer1.initialize(G_HALF_PERIOD * 1e06);
  Timer1.attachInterrupt(blinkGreen);
}


void loop() {
  digitalWrite(RLED_PIN, redLedState);
  redLedState = !redLedState;
  serialPrintStatus(); //The read of the serial port will be synchronous
  delay(R_HALF_PERIOD * 1e03);
}
