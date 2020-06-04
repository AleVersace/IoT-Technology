//Lab1.1 - 2 leds alternating using the loop() and an ISR connected to a timer
#include <TimerOne.h>

//Insert as constant the number of the PINs used
const int RLED_PIN=12;
const int GLED_PIN=11;

//Define the half period of the two leds
const float R_H_PERIOD=1.5;
const float G_H_PERIOD=3.5;

//Set initial state of the leds as LOW
int stateG=LOW;
int stateR=LOW;

//ISR function
void blinkGreen(){
  stateG=!stateG; //Invert the green led state
  digitalWrite(GLED_PIN,stateG);
}

void setup() {
  pinMode(RLED_PIN,OUTPUT);
  pinMode(GLED_PIN,OUTPUT);
  Timer1.initialize(G_H_PERIOD*1e06); //Set the trigger time in microseconds
  Timer1.attachInterrupt(blinkGreen); //Attach the function blinkGreen() to Timer1
}

void loop() {
  stateR=!stateR; //Invert the red led state
  digitalWrite(RLED_PIN,stateR);
  delay(R_H_PERIOD*1e03);
}
