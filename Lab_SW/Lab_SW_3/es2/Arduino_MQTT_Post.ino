#include <MQTTclient.h>
#include <ArduinoJson.h>
#include <Process.h>


const int capacity1 = JSON_OBJECT_SIZE(2) + JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(4) + 40;
const int capacity2 = JSON_OBJECT_SIZE(2) + JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc_snd(capacity1);
DynamicJsonDocument doc_rec(capacity2);

const String url = "http://10.0.0.10:8080/devices";
const String id = "A8:40:41:1A:60:B0";

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
  digitalWrite(INT_LED_PIN, LOW);
  Bridge.begin();
  digitalWrite(INT_LED_PIN, HIGH);
  mqtt.begin("test.mosquitto.org", 1883);
}

void loop() {
  mqtt.monitor();
  code = postRequest(senMlEncodeRegister());
  String message = senMlEncodeSensor("Temperature", (float)((int)(actualTemp() * 100))/100, "Cel");
  Serial.println(message);
  mqtt.publish(my_base_topic + String("/temp"), message);

  delay(8000);
}


// Send POST request using curl on Yun linux chip.
int postRequest(String data) {
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("POST");
  p.addParameter("-d");
  p.addParameter(data);
  p.addParameter(url);
  p.run();

  return p.exitValue(); // Status curl command
}

// Encode in senMl using a dynamic Json Document and Arduino Json
String senMlEncodeSensor(String res, float v, String unit) {
  doc_rec.clear();

  doc_snd["bn"] = "Gruppo 13";
  doc_snd["e"][0]["n"] = res;
  if (unit != "") {
    doc_snd["e"][0]["u"] = unit;
  } else {
    doc_snd["e"][0]["u"] = (char*) NULL;
  }

  doc_snd["e"][0]["t"] = millis();
  doc_snd["e"][0]["v"] = v;

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


// Registration to Catalog
String senMlEncodeRegister() {
  doc_rec.clear();
  doc_rec["id"] = id;
  doc_rec["endpoints"]["temp"] = "/tiot/13/temp";
  doc_rec["resources"] = "temp";

  String output;
  serializeJson(doc_rec, output);
  return output;
}
