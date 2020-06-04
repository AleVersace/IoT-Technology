#include <MQTTclient.h>
#include <ArduinoJson.h>

const int capacity = JSON_OBJECT_SIZE(2) + JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc_snd(capacity);
DynamicJsonDocument doc_rec(capacity);

const String my_base_topic = "/tiot/13";
int code = 0;
int INT_LED_PIN=13;

// TEMP
const int TMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

// LED
const int LED_PIN = 9;

void setup() {
  pinMode(TMP_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  Serial.begin(9600);
  while(!Serial);
  digitalWrite(INT_LED_PIN, LOW);
  Bridge.begin();
  digitalWrite(INT_LED_PIN, HIGH);
  mqtt.begin("test.mosquitto.org", 1883);
  mqtt.subscribe(my_base_topic + String("/led"), setLedValue);
}

void loop() {
  mqtt.monitor();
  String message = senMlEncode("Temperature", (float)((int)(actualTemp() * 100))/100, "Cel");
  mqtt.publish(my_base_topic + String("/temperature"), message);

  delay(1000);
}


void setLedValue(const String& topic, const String& subtopic, const String& message) {
  Serial.println("eccoci");
  DeserializationError err = deserializeJson(doc_rec, message);
  if(err) {
    Serial.print("deserializeJson() failed with code ");
    Serial.println(err.c_str());
  }
  if(doc_rec["e"][0]["n"] == "led") {
    if(doc_rec["e"][0]["t"] == (char *)NULL && doc_rec["e"][0]["u"] == (char *)NULL) {
      int statusLed = doc_rec["e"][0]["v"];
      if(statusLed == 0 || statusLed == 1) {
        digitalWrite(LED_PIN, statusLed);
      }else {
        Serial.println("Valore non supportato.");
      }
    }else {
      Serial.println("Timestamp o unità di misura non supportate.");
    }
  }else {
    Serial.println("Elemento non supportato.");
  }
}

// Encode in senMl using a dynamic Json Document and Arduino Json
String senMlEncode(String res, float v, String unit) {
  doc_snd.clear();

  doc_snd["bn"] = "Gruppo 13";
    doc_snd["e"][0]["t"] = millis();
  doc_snd["e"][0]["n"] = res;
  
  doc_snd["e"][0]["v"] = v;
  if (unit != "") {
    doc_snd["e"][0]["u"] = unit;
  } else {
    doc_snd["e"][0]["u"] = (char*) NULL;
  }



  String output;
  serializeJson(doc_snd, output);
  return output;
}

// Calculate temp using sensor
float actualTemp() {
  float temp = analogRead(TMP_PIN);
  float R = (Vcc / temp - 1) * R0;
  float T = 1 / (log(R / R0) / B + 1.0 / T0);
  float Tfin = T - 273.15;
  return Tfin;
}
