//Lab1.5 - Rad of the temperature using the Grove sensor

#include <math.h>

//Define the analog pin of the sensor
const int TMP_PIN = A1;

//Define all the constants needed for the conversion
const float B = 4275.0;
const long int R0 = 100000;
const float T0 = 298.0;

void setup() {
  Serial.begin(9600);     //Initialize serial port
  while (!Serial);
  Serial.println("Lab 1.4 Starting");     //Welcome
  pinMode(TMP_PIN, INPUT);      //The sensor will send data to the Arduino
}

void loop() {
  //Conversion steps
  float val = analogRead(TMP_PIN);
  float R = (1023.0 / val - 1) * R0;
  float T = 1 / (log(R / R0) / B + 1 / T0);

  //Convert from K to C
  float Tfin = T - 273.15;
  Serial.println(Tfin);     //Print of serial monitor the value
  delay(10000);
}
