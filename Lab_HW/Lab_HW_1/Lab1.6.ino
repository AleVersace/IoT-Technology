//Lab1.6 - Read of temperature and show it on LCD screen
#include <LiquidCrystal_PCF8574.h>
#include <math.h>

LiquidCrystal_PCF8574 lcd(0x27);      //Define the address of the monitor for the I2C connection

const int TMP_PIN = A1;     //Define the pin of the temperature sensor

//Define all conversion constant
const int B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

void setup() {
  //Set up of the display
  lcd.begin(16, 2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  lcd.print("Temperature:");
  pinMode(TMP_PIN, INPUT);
}

void loop() {
  //Conversion to temperature
  float val = analogRead(TMP_PIN);
  float R = (Vcc / val - 1) * R0;
  float T = 1 / (log(R / R0) / B + 1.0 / T0);
  float Tfin = T - 273.15;

  //In order not to re-write every time "Temperature:" we set the curson to overwrite only the temperature value
  lcd.setCursor(12, 0);
  lcd.print(Tfin);
  delay(10000);
}
