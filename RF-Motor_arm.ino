#include <SPI.h>
#include <RF24.h>
#include <Servo.h>

// RF24 Pins
#define CE_PIN 9
#define CSN_PIN 10

// Motor Pins
const int IN1 = 2;    
const int IN2 = 3;    
const int ENA = 5;    
const int IN3 = 4;    
const int IN4 = 7;    
const int ENB = 6;    

// Servo Pins
const int SERVO1_PIN = 8;
const int SERVO2_PIN = 12;
const int SERVO3_PIN = 13;

// Speed (0-255)
int speedVal = 200;

// RF Pipes (telemetry only)
const uint64_t pipes[2] = { 0xF0F0F0F0D2LL, 0xF0F0F0F0E1LL };
RF24 radio(CE_PIN, CSN_PIN);

struct TelemetryData {
  float temperature;
  float humidity;
  int tagId;
  uint32_t timestamp;
};
TelemetryData telemetry;

// Servo setup
Servo servo1, servo2, servo3;
int angle1 = 90, angle2 = 90, angle3 = 90;

enum Command {
  CMD_FORWARD, CMD_REVERSE, CMD_LEFT, CMD_RIGHT,
  CMD_STOP, CMD_COAST, CMD_SPEED_UP, CMD_SPEED_DOWN,
  CMD_NONE
};

void setup() {
  Serial.begin(115200);

  // Motor pins
  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT); pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT); pinMode(ENB, OUTPUT);

  // Servo pins
  servo1.attach(SERVO1_PIN);
  servo2.attach(SERVO2_PIN);
  servo3.attach(SERVO3_PIN);
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  // RF for telemetry
  if (!radio.begin()) {
    Serial.println("Radio not responding!");
    while (1);
  }
  radio.setPALevel(RF24_PA_LOW);
  radio.setChannel(76);
  radio.setDataRate(RF24_250KBPS);
  radio.enableDynamicPayloads();
  radio.setRetries(5, 15);
  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1, pipes[0]);
  radio.startListening();

  Serial.println("System ready - use W/A/S/D for motors, Q/W/A/S/Z/X for servos");
  brake();
}

void loop() {
  if (Serial.available()) {
    char input = Serial.read();
    input = tolower(input);
    
    if (isMotorCommand(input)) {
      Command cmd = decodeMotorCommand(input);
      executeMotorCommand(cmd);
    } else {
      updateServoAngles(input);
    }

    sendTelemetry();
  }
}

// --- Motor Logic ---
bool isMotorCommand(char c) {
  return c == 'w' || c == 'a' || c == 's' || c == 'd' || c == ' ' || c == 'c' || c == '+' || c == '-';
}

Command decodeMotorCommand(char c) {
  switch (c) {
    case 'w': return CMD_FORWARD;
    case 's': return CMD_REVERSE;
    case 'a': return CMD_LEFT;
    case 'd': return CMD_RIGHT;
    case ' ': return CMD_STOP;
    case 'c': return CMD_COAST;
    case '+': return CMD_SPEED_UP;
    case '-': return CMD_SPEED_DOWN;
    default: return CMD_NONE;
  }
}

void executeMotorCommand(Command cmd) {
  switch (cmd) {
    case CMD_FORWARD:
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("Moving FORWARD"); break;
      
    case CMD_REVERSE:
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("Moving REVERSE"); break;

    case CMD_LEFT:
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("Turning LEFT"); break;

    case CMD_RIGHT:
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("Turning RIGHT"); break;

    case CMD_STOP:
      brake();
      Serial.println("BRAKING"); break;

    case CMD_COAST:
      digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
      analogWrite(ENA, 0); analogWrite(ENB, 0);
      Serial.println("COASTING"); break;

    case CMD_SPEED_UP:
      speedVal = constrain(speedVal + 10, 0, 255);
      Serial.print("Speed: "); Serial.println(speedVal); break;

    case CMD_SPEED_DOWN:
      speedVal = constrain(speedVal - 10, 0, 255);
      Serial.print("Speed: "); Serial.println(speedVal); break;

    default: break;
  }
}

void brake() {
  digitalWrite(IN1, HIGH); digitalWrite(IN2, HIGH);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, HIGH);
  analogWrite(ENA, 0); analogWrite(ENB, 0);
}

void updateServoAngles(char input) {
  switch (input) {
    case 'u': angle1 = constrain(angle1 + 5, 0, 180); break;
    case 'j': angle1 = constrain(angle1 - 5, 0, 180); break;
    case 'i': angle2 = constrain(angle2 + 5, 0, 180); break;
    case 'k': angle2 = constrain(angle2 - 5, 0, 180); break;
    case 'o': angle3 = constrain(angle3 + 5, 0, 180); break;
    case 'l': angle3 = constrain(angle3 - 5, 0, 180); break;
    default: return;
  }

  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  Serial.print("Servo angles: ");
  Serial.print(angle1); Serial.print(", ");
  Serial.print(angle2); Serial.print(", ");
  Serial.println(angle3);
}

// --- Telemetry ---
void sendTelemetry() {
  telemetry.temperature = 25.0 + random(-50, 50) / 10.0;
  telemetry.humidity = 60.0 + random(-100, 100) / 10.0;
  telemetry.tagId = 1;
  telemetry.timestamp = millis();

  radio.stopListening();
  bool success = radio.write(&telemetry, sizeof(telemetry));
  if (success) Serial.println("Telemetry sent.");
  else Serial.println("Telemetry failed.");
  radio.startListening();
}
