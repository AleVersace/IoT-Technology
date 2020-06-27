#include <Bridge.h>
#include <ArduinoJson.h>
#include <Process.h>

const int capacity = JSON_OBJECT_SIZE(2) + JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc_snd(capacity);

const String url = "http://10.0.0.4:8080/log";
int code = 0;
int INT_LED_PIN=13;

// TEMP
const int TMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

void setup() {
  pinMode(TMP_PIN, INPUT);
  Serial.begin(9600);
  while(!Serial);
  digitalWrite(INT_LED_PIN, LOW);
  Bridge.begin();
  digitalWrite(INT_LED_PIN, HIGH);
}

void loop() {
  code = postRequest(senMlEncode("Temperature", (float)((int)(actualTemp() * 100))/100, "Cel"));
  if(code == 1) {
    Serial.println("Errore curl command");
  }
  Serial.println(code);
  delay(1000);
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
String senMlEncode(String res, float v, String unit) {
  doc_snd.clear();

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
