//Lab 1.4 - Modify the speed of a DC motor using the serial port

const int FAN_PIN = 6;      //Pin of the DC motor
float current_speed = 0;      //Speed starts from 0
const float inc = 25.5;     //Increment constant


void changeSpeed() {
  //Check if there is something in the buffer
  if (Serial.available() > 0) {
    int signal = Serial.read();
    if (signal == 43) {    //If read the ASCII value of '+'
      
      if (current_speed < 255) {     //If speed is not at the maximum
        current_speed += inc;     //Increment speed
        analogWrite(FAN_PIN, (int) current_speed);      //Write on the motor pin the new speed
        Serial.println("Increase speed: " + String(current_speed));
      }
      else {      //If speed at maximum (255)
        Serial.println("Already at maximum!");
      }
      
    }
    
    else if (signal == 45) {      //If read the ASCII value of '-'
      if (current_speed > 0) {      //If speed is not zero
        current_speed -= inc;     //Decrease speed
        analogWrite(FAN_PIN, (int) current_speed);
        Serial.println("Decrease speed: " + String(current_speed));
      }
      else {      //If speed already at zero
        Serial.println("Already at minimum!");
      }
    }
    
    else {      //Value read is not + or -
      Serial.println("Error - command not valid [+,-]");
    }
  }
}

void setup() {
  Serial.begin(9600);     //Initialize serial comunication
  while (!Serial);
  Serial.println("Lab 1.4 Starting");     //Welcome
  pinMode(FAN_PIN, OUTPUT);
  analogWrite(FAN_PIN, (int) current_speed);      //Set the initial speed
}

void loop() {
  changeSpeed();
}
