//Lab1.3 - Observe movements using the motion sensor HC-SR501

const int RLED_PIN = 12;      //Set pin of the led
const int PIR_PIN = 7;      //Set pin of the HC-SR501 sensor

int redLedState = LOW;      //Initial state of led set to LOW
volatile int tot_count = 0;     //Volatile because used by ISR and loop()

//ISR that checks if a movement has been detected
void checkPresence() {
  int status = digitalRead(PIR_PIN);      //Read the value of the sensor
  redLedState = status;
  digitalWrite(RLED_PIN, redLedState);      //Set the value of the led equal to the value read from the sensor
  if (status == HIGH) {     //If a rising edge is detected then increase the counter
    tot_count += 1;
  }
}


void setup() {
  Serial.begin(9600);     //Initialize serial monitor
  while (!Serial);    //loop won't start untill serial monitor is open
  Serial.println("Lab 1.3 Starting");     //Welcome message
  pinMode(PIR_PIN, INPUT);      //The sensor will send data to Arduino, so il will be seen as input
  pinMode(RLED_PIN, OUTPUT);
  attachInterrupt(digitalPinToInterrupt(PIR_PIN), checkPresence, CHANGE);     //Call the function checkPresence() when a change occurs on the value of PIR_PIN
}

void loop() {
  Serial.println(String(tot_count));    //Print the total count every 30s
  delay(30 * 1e03);
}
