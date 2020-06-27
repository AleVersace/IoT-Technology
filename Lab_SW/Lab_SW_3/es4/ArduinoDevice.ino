#include <math.h>
#include <LiquidCrystal_PCF8574.h>
#include <MQTTclient.h>
#include <ArduinoJson.h>
#include <Process.h>

LiquidCrystal_PCF8574 lcd(0x27);

const String url = "http://10.0.0.10:8080";
const String id = "id1";
String broker = "";
String port = "0";
int flag = 0;

const String my_base_topic = "/iot/13";
int code = 0;

// Fan
const int FAN_PIN = 6;

// Temp
const int TEMP_PIN = A1;
const float B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

// Led
const int LED_PIN = 9;

// Pir
const int PIR_PIN = 7;

//Sound
const int SOUND_PIN = 4;


unsigned long lastPost = -30000;


void setup() {
  Serial.begin(9600);
  Bridge.begin();
  //GPIO definition
  pinMode(FAN_PIN, OUTPUT);
  pinMode(SOUND_PIN, INPUT);
  analogWrite(FAN_PIN, 0);
  pinMode(TEMP_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(PIR_PIN, INPUT);
  getBroker();

  //LCD initialization
  lcd.begin(16, 2);

  lcd.setBacklight(255);
  lcd.home();
  lcd.clear();
  lcd.print("Welcome");
  mqtt.begin(broker, atoi(port.c_str()));
  mqtt.subscribe("/iot/13/a/#", getMQQTdata);
}

void loop() {
  //Registra al catalog;
  if (millis() - lastPost > 30000) {
    int code = postRequest();
    lastPost = millis();
  }

  float temp = analogRead(TEMP_PIN);
  int noise = digitalRead(SOUND_PIN);
  
  int movement = digitalRead(PIR_PIN);
  Serial.println(movement);
  mqtt.monitor();
  mqtt.publish(my_base_topic + String("/tmp"), senMlEncodeSensor("Temp", temp, "\"Cel\""));
  mqtt.publish(my_base_topic + String("/mov"), senMlEncodeSensor("Move", movement, "null"));
  mqtt.publish(my_base_topic + String("/nos"), senMlEncodeSensor("Nois", noise, "null"));
  delay(10);
}



// Send POST request using curl on Yun linux chip.
int postRequest() {
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("POST");
  p.addParameter("-d");
  p.addParameter(F("{\"id\":\"ID1\",\"ep\":{\"tmp\":\"/iot/13/tmp\",\"nos\":\"/iot/13/nos\",\"mov\":\"/iot/13/mov\",\"lcd\":\"/iot/13/a/d\",\"led\":\"/iot/13/a/l\",\"fan\":\"/iot/13/a/f\"}}"));
  p.addParameter("http://10.0.0.10:8080/devices");
  p.run();
  return p.exitValue(); // Status curl command
}



//uncode in senMl using a dynamic Json Document and Arduino Json
String senMlEncodeSensor(String res, float v, String unit) {
  String formatted = "{\"bn\":\"G13\",\"e\":[{\"t\":" + String(millis()) + ",\"n\":\"" + res + "\",\"v\":" + v + ",\"u\":" + unit + "}]}";
  return formatted;
}


int getBroker() {
  Process p;
  p.begin("curl");
  p.addParameter(" - H");
  p.addParameter("Content - Type: application / json");
  p.addParameter(" - X");
  p.addParameter("GET");
  p.addParameter(url + "/broker/name");
  p.run();
  String result = "";
  while (p.available() > 0) {
    result = result + char(p.read());
  }
  broker = String(result);

  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("GET");
  p.addParameter(url + "/broker/port");
  p.run();
  result = "";
  while (p.available() > 0) {
    result = result + char(p.read());
  }
  port = String(result);
  return p.exitValue(); // Status curl command
}

void getMQQTdata(const String& topic, const String& subtopic, const String& message) {
  if (subtopic == "d") {
    lcd.clear();
    lcd.home();
    if (message.length() > 16) {
      for (int i = 0; i < 16; i++) {
        lcd.print(message[i]);
      }
      lcd.setCursor(0, 1);
      for (int i = 16; i < message.length(); i++) {
        lcd.print(message[i]);
      }
    }
    else {
      lcd.print(message);
    }
  }

  else if (subtopic == "f") {
    int speedFan = atoi(message.c_str());
    analogWrite(FAN_PIN, speedFan);
  }
  else if (subtopic == "l") {
    int ledPower = atoi(message.c_str());
    analogWrite(LED_PIN, ledPower);
  }

}
