#include <Bridge.h>
#include <BridgeServer.h>
#include <BridgeClient.h>
#include <ArduinoJson.h>

BridgeServer server;

int const INT_LED_PIN = 13;
int const LED_PIN = 9;
const int capacity = JSON_OBJECT_SIZE(2) + JSON_ARRAY_SIZE(1) + JSON_OBJECT_SIZE(4) + 40;
DynamicJsonDocument doc_snd(capacity);

// TEMP
const int TMP_PIN = A1;
const int B = 4275;
const long int R0 = 100000;
const float Vcc = 1023.0;
const float T0 = 298.0;

void setup() {
  pinMode(TMP_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(INT_LED_PIN, OUTPUT);
  digitalWrite(INT_LED_PIN, LOW);
  Bridge.begin();
  digitalWrite(INT_LED_PIN, HIGH);
  server.listenOnLocalhost();
  server.begin();
}

void loop() {
  BridgeClient client = server.accept();

  if (client) {
    process(client);
    client.stop();
  }

  delay(50);

}

// Parse requests recived
void process(BridgeClient client) {
  String command = client.readStringUntil('/');
  command.trim();

  if (command == "led" || command == "temperature") {

    // LED
    if (command == "led") {
      int val = client.parseInt();
      if (val == 0 || val == 1) {
        digitalWrite(LED_PIN, val);
        printResponse(client, 200, senMlEncode("led", val, ""));
      } else {
        printResponse(client, 400, "Error");
      }
    }

    // TEMP
    if (command == "temperature") {
      printResponse(client, 200, senMlEncode("temperature", actualTemp(), "Cel"));
    }

  } else {
    printResponse(client, 400, "Error 404 - URI not found!");
  }
}

// Create response to the request recived
void printResponse(BridgeClient client, int code, String body) {
  client.println("Status: " + String(code));
  if (code == 200) {
    client.println("Content-type: application/json; charset=utf-8");
    client.println();
    client.println(body);
  }
  else if (code == 400) {
    client.println("Content-type: application/json; charset=utf-8");
    client.println();
    client.println(body);
  }
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
  Serial.println(Tfin);
  return Tfin;
}
