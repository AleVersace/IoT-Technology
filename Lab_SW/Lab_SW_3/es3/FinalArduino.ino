#include <MQTTclient.h>
#include <ArduinoJson.h>
#include <Process.h>

const String url = "http://10.0.0.10:8080/devices";
const String id = "A8:40:41:1A:60:B0";
String broker = "";
String port ="0";
int flag = 0;

const int capacity3 = JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(2) + JSON_OBJECT_SIZE(4) + 30;


const String my_base_topic = "/tiot/13";
int code = 0;
int INT_LED_PIN = 13;

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
  while (!Serial);
  digitalWrite(INT_LED_PIN, LOW);
  Bridge.begin();
  getBroker();
  digitalWrite(INT_LED_PIN, HIGH);
  mqtt.begin(broker, atoi(port.c_str()));
  mqtt.subscribe(my_base_topic + String("/led"), setLedValue);
}

void loop() {
  mqtt.monitor();
  String message = senMlEncodeSensor("Temperature", (float)((int)(actualTemp() * 100)) / 100, "Cel");
  Serial.println(message);
  mqtt.publish(my_base_topic + String("/temp"), message);
  code = postRequest(senMlEncodeRegister());
  delay(3000);
}


void setLedValue(const String& topic, const String& subtopic, const String& message) {
  DynamicJsonDocument doc_rec(capacity3);
  DeserializationError err = deserializeJson(doc_rec, message);
  if (err) {
    Serial.print("deserializeJson() failed with code ");
    Serial.println(err.c_str());
  }
  if (doc_rec["e"][0]["n"] == "led") {
    if (doc_rec["e"][0]["t"] == (char *)NULL && doc_rec["e"][0]["u"] == (char *)NULL) {
      int statusLed = doc_rec["e"][0]["v"];
      if (statusLed == 0 || statusLed == 1) {
        digitalWrite(LED_PIN, statusLed);
      } else {
        Serial.println("Valore non supportato.");
      }
    } else {
      Serial.println("Timestamp o unità di misura non supportate.");
    }
  } else {
    Serial.println("Elemento non supportato.");
  }
}

//ùncode in senMl using a dynamic Json Document and Arduino Json
String senMlEncodeSensor(String res, float v, String unit) {
  StaticJsonDocument<70> doc_snd;
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


//Registration to Catalog
String senMlEncodeRegister() {
  StaticJsonDocument<70> doc_reg;
  doc_reg.clear();
  doc_reg["id"] = id;
  doc_reg["endpoints"]["temp"] = "/tiot/13/temp";
  doc_reg["endpoints"]["led"] = "/tiot/13/led";
  JsonArray vet = doc_reg.createNestedArray("resources");
  vet.add("temp");
  vet.add("led");

  String output;
  serializeJson(doc_reg, output);
  return output;
}

int getBroker() {
  Process p;
  p.begin("curl");
  p.addParameter("-H");
  p.addParameter("Content-Type: application/json");
  p.addParameter("-X");
  p.addParameter("GET");
  p.addParameter("http://10.0.0.10:8080/broker/name");
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
  p.addParameter("http://10.0.0.10:8080/broker/port");
  p.run();
  result = "";
  while (p.available() > 0) {
    result = result + char(p.read());
  }
  port = String(result);
  return p.exitValue(); // Status curl command
}
