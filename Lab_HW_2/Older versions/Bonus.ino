#include <math.h>
#include <TimerOne.h>
#include <LiquidCrystal_PCF8574.h>

const int PIN_LED_GREEN = 8;
int status_led_green = LOW;

LiquidCrystal_PCF8574 lcd(0x27);

volatile unsigned long timeStart = 0;
unsigned long last_clap = 0;
unsigned long first_clap = 0;


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
const int LED_PIN = 5;

// Temp Range Fan
float FTEMP_MIN[] = {25, 20};
float FTEMP_MAX[] = {30, 25};

// Temp Range Led
float LTEMP_MIN[] = {10.0, 15.0};
float LTEMP_MAX[] = {15.0, 20.0};

// Pir
const int PIR_PIN = 7;
volatile int PIR_presence;

//Sound sensor
int SOUND_counter = 0;
int SOUND_presence = 0;
const int SOUND_PIN = 11;
int status_sound = 0;
const int n_sound_events = 5;
const int sound_interval = 10000;
unsigned long timerSound = 0;
volatile int presence = 0;

int num_display = 0;
int last = 0;

int perc_AC = 0;
int perc_HT = 0;


void setup() {
  Serial.begin(9600);
  while (!Serial);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(SOUND_PIN, INPUT);
  analogWrite(FAN_PIN, 0);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  digitalWrite(PIN_LED_GREEN, LOW);
  timeStart = millis();
  timerSound = timeStart;
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), checkPresence, RISING);


  lcd.begin(16, 2);
  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();

}

void loop() {
  perc_AC = regulate_fan_or_led(FAN_PIN, FTEMP_MIN[presence], FTEMP_MAX[presence]);
  perc_HT = regulate_fan_or_led(LED_PIN, LTEMP_MAX[presence], LTEMP_MIN[presence]);
  serialSet_Point();
  //  Serial.print(FTEMP_MIN[0]);
  //  Serial.print("");
  //  Serial.println(FTEMP_MAX[0]);

  unsigned long now = millis();
  if (now - timeStart > 15000) {
    PIR_presence = 0;
  }

  status_sound = digitalRead(SOUND_PIN);

  if (status_sound == HIGH && (now - last_clap) > 200) {
    SOUND_counter += 1;
    if (SOUND_counter == 1) {
      first_clap = millis();
      checkPresence();
    }
    if (millis()-first_clap > 500) {
      SOUND_counter=0;
    }
    if (SOUND_counter == 2) {
      status_led_green = digitalRead(PIN_LED_GREEN);
      digitalWrite(PIN_LED_GREEN, !status_led_green);
      SOUND_counter = 0;
    }
    last_clap = millis();
    //Serial.println(SOUND_counter);

  }

  status_led_green=digitalRead(PIN_LED_GREEN);
  if(PIR_presence==0 && status_led_green==HIGH){
    status_led_green=LOW;
    digitalWrite(PIN_LED_GREEN, status_led_green);
    }

  //  unsigned long now2 = millis();
  //  if (now2 - timerSound > sound_interval) {
  //    timerSound = millis();
  //    if (SOUND_counter < n_sound_events) {
  //      SOUND_counter = 0;
  //      SOUND_presence = 0;
  //      //Serial.println("No sound for 10 seconds - no presence");
  //    }
  //    else {
  //      //Serial.println("Too many movements - still presence");
  //      SOUND_counter = 0;
  //      SOUND_presence = 1;
  //    }
  //  }


  //  if (SOUND_presence == 1 | PIR_presence == 1) {
  //    presence = 1;
  //  }
  //  else {
  //    presence = 0;
  //  }
  //Serial.println(presence);
  changeDisplay(millis());

}

// 1) Regulate fan speed or led color depending on the temperature
int regulate_fan_or_led(int PIN, int min, int max) {
  float temp = actualTemp();
  if (temp >= min && temp <= max) {
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

// Check
void checkPresence() {
  PIR_presence = 1;
  timeStart = millis();
}

void serialSet_Point() {
  if (Serial.available() > 0) {
    String signal = Serial.readString();
    String command = signal.substring(0, 14);
    String range1 = signal.substring(15, 17);
    String range2 = signal.substring(18);

    Serial.println(command);
    Serial.println(range1);
    Serial.println(range2);

    if (command.equals("RANGE_FAN_PRES")) {
      FTEMP_MIN[1] = range1.toFloat();
      FTEMP_MAX[1] = range2.toFloat();
    }
    else if (command.equals("RANGE_FAN_ABSN")) {
      FTEMP_MIN[0] = range1.toFloat();
      FTEMP_MAX[0] = range2.toFloat();
    }
    else if (command.equals("RANGE_LED_PRES")) {
      LTEMP_MIN[1] = range1.toFloat();
      LTEMP_MAX[1] = range2.toFloat();
    }
    else if (command.equals("RANGE_LED_ABSN")) {
      LTEMP_MIN[0] = range1.toFloat();
      LTEMP_MAX[0] = range2.toFloat();
    }
    else {
      Serial.println("Command Error!");
    }
  }
}

void changeDisplay(int now) {
  if (now - last > 5000) {
    last = millis();
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
