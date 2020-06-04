#include <math.h>
#include <TimerOne.h>
#include <LiquidCrystal_PCF8574.h>

LiquidCrystal_PCF8574 lcd(0x27);

// Fan
const int FAN_PIN = 6;
const int MAX_SPEED = 255;

// Temp
const int TEMP_PIN = A1;
const float B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

// Led
const int LED_PIN = 9;

// Temp Range Fan
float FTEMP_MIN[] = {25, 20};
float FTEMP_MAX[] = {30, 25};

// Temp Range Led
float LTEMP_MIN[] = {10, 15};
float LTEMP_MAX[] = {15, 20};

// Pir
const int PIR_PIN = 7;
volatile int PIR_presence;
volatile unsigned long timeStartMovement = 0;

//Sound sensor
int SOUND_counter = 0;
int SOUND_presence = 0;
const int SOUND_PIN = 11;
const int SOUND_interval = 5000;
const int SOUND_timeout = 15000;
unsigned long vetSounds[] = {0.0, 0.0, 0.0, 0.0};
unsigned long startFlag = 0;

volatile int presence = 0;

//Display
int num_display = 0;
int lastChangeDisplay = 0;



void setup() {
  Serial.begin(9600);
  while (!Serial);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(SOUND_PIN, INPUT);
  analogWrite(FAN_PIN, 0);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  timeStartMovement = millis();
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), checkPresencePIR, RISING);
  lcd.begin(16, 2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  lcd.print("Starting...");

}

void loop() {
  //Compute the value from 0 to 255 of the FAN or LED to be send and return the value in order to use it in the display
  int perc_AC = regulate_fan_or_led(FAN_PIN, FTEMP_MIN[presence], FTEMP_MAX[presence]);
  int perc_HT = regulate_fan_or_led(LED_PIN, LTEMP_MAX[presence], LTEMP_MIN[presence]);

  //Read from the serial port the command to update the set points
  serialSet_Point();

  //If from the last movement 15 sec are passed, then turn to 0 the PIR_presence
  if (millis() - timeStartMovement > 15000) {
    PIR_presence = 0;
  }

  //Check if a number of sounds are detected in a given intervall
  checkPresenceSOUND();

  //If one of the two sensor detect presence then the variable presence is set to 1
  if (SOUND_presence == 1 || PIR_presence == 1) {
    presence = 1;
  }
  else {
    presence = 0;
  }
  
  //Change display info every 5 seconds
  changeDisplay(millis(), perc_AC, perc_HT);
}



//Regulate fan speed or led color depending on the temperature
int regulate_fan_or_led(int PIN, int min, int max) {
  float temp = actualTemp();
  if ((temp >= min && temp <= max && PIN == FAN_PIN) || (temp <= min && temp >= max && PIN == LED_PIN)) {
    int value = (int) MAX_SPEED / (max - min) * (temp - min);
    analogWrite(PIN, value);
    return value;
  }

  else if ((PIN == FAN_PIN && temp < min) || (PIN == LED_PIN && temp > min)) {
    analogWrite(PIN, 0);
    return 0;
  }
  else {
    analogWrite(PIN, MAX_SPEED);
    return MAX_SPEED;
  }

}

// Calculate temp using sensor
float actualTemp() {
  float temp = analogRead(TEMP_PIN);
  float R = (Vcc / temp - 1) * R0;
  float T = 1 / (log(R / R0) / B + 1.0 / T0);
  float Tfin = T - 273.15;
  return Tfin;
}

// Function called by the ISR of the PIR every time a movement is detected
void checkPresencePIR() {
  PIR_presence = 1;
  timeStartMovement = millis();
}

//The SOUND sensor has to check if a number of events happen in a given period of time
void checkPresenceSOUND() {
  int status_sound = digitalRead(SOUND_PIN);
  unsigned long now = millis();
  if (status_sound == HIGH && (now - vetSounds[3]) > 200) {
    unsigned long first = vetSounds[0];
    memcpy(vetSounds, &vetSounds[1], sizeof(vetSounds) - sizeof(unsigned long));
    vetSounds[3] = now;
    if (now - first < SOUND_interval && SOUND_counter > 3) {
      SOUND_presence = 1;
      startFlag = millis();
    }
    SOUND_counter++;
  }
  if (millis() - startFlag > SOUND_timeout && SOUND_presence == 1) {
    SOUND_presence = 0;
  }
}

void serialSet_Point() {
  if (Serial.available() > 0) {
    String signal = Serial.readString();
    String command = signal.substring(0, 14);
    String range1 = signal.substring(15, 17);
    String range2 = signal.substring(18);

    if (command.equals("RANGE_FAN_PRES")) {
      FTEMP_MIN[1] = range1.toFloat();
      FTEMP_MAX[1] = range2.toFloat();
      Serial.println("Range of the FAN in case of PRESENCE has beeen successfully updated!");
    }
    else if (command.equals("RANGE_FAN_ABSN")) {
      FTEMP_MIN[0] = range1.toFloat();
      FTEMP_MAX[0] = range2.toFloat();
      Serial.println("Range of the FAN in case of NO PRESENCE has beeen successfully updated!");
    }
    else if (command.equals("RANGE_LED_PRES")) {
      LTEMP_MIN[1] = range1.toFloat();
      LTEMP_MAX[1] = range2.toFloat();
      Serial.println("Range of the LED in case of PRESENCE has beeen successfully updated!");
    }
    else if (command.equals("RANGE_LED_ABSN")) {
      LTEMP_MIN[0] = range1.toFloat();
      LTEMP_MAX[0] = range2.toFloat();
      Serial.println("Range of the LED in case of NO PRESENCE has beeen successfully updated!");
    }
    else {
      Serial.println("Command Error!");
      Serial.println("Please insert a command of the form RANGE_[FAN|LED]_[PRES|ABSN]=MIN/MAX");
    }
  }
}

//Every 5 second update the display
void changeDisplay(int now, int perc_AC, int perc_HT) {
  if (now - lastChangeDisplay > 5000) {
    lastChangeDisplay = millis();
    if (num_display == 0) {
      num_display = 1;
      lcd.home();
      lcd.clear();
      lcd.print("T:");
      float temp = round(actualTemp());
      lcd.print(temp);
      lcd.print(" Pres:" + String(presence));
      lcd.setCursor(0, 1);
      lcd.print("AC:" + String(100 * perc_AC / 255) + "% HT:" + String(100 * perc_HT / 255) + "%");
    }
    else {
      num_display = 0;
      lcd.home();
      lcd.clear();
      lcd.print("AC m:");
      lcd.print(FTEMP_MIN[presence], 1);
      lcd.print(" M:");
      lcd.print(FTEMP_MAX[presence], 1);
      lcd.setCursor(0, 1);
      lcd.print("HT m:");
      lcd.print(LTEMP_MIN[presence], 1);
      lcd.print(" M:");
      lcd.print(LTEMP_MAX[presence], 1);
    }
  }
}
