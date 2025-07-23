#include <SPI.h>
#include <RF24.h>

// RF24 Pins
#define CE_PIN  9
#define CSN_PIN 10

// Motor Pins
const int IN1 = 6;    // Left motor dir A1 (non‑PWM)
const int IN2 = 7;    // Left motor dir A2 (PWM‑capable)
const int ENA = 5;    // Left motor speed (PWM)
const int IN3 = 8;    // Right motor dir B1 (non‑PWM)
const int IN4 = 9;    // Right motor dir B2 (PWM‑capable)
const int ENB = 10;   // Right motor speed (PWM)

// RF setup (unused here)
RF24 radio(CE_PIN, CSN_PIN);
const uint64_t pipes[2] = { 0xF0F0F0F0D2LL, 0xF0F0F0F0E1LL };

// Telemetry structure (unused here)
struct TelemetryData {
  float   temperature;
  float   humidity;
  int     tagId;
  uint32_t timestamp;
} telemetry;

void setup() {
  Serial.begin(9600);
  delay(100);
  Serial.println("Initializing...");

  // Motor pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  Serial.println("Ready. Serial: W/A/S/D = drive, F = brake");
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    cmd = toupper(cmd);
    Serial.print("Cmd: ");
    Serial.println(cmd);

    switch (cmd) {
      case 'W':  // Forward
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);  analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);  analogWrite(ENB, 200);
        Serial.println("→ FORWARD");
        break;

      case 'S':  // Reverse
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);   analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);   analogWrite(ENB, 200);
        Serial.println("← REVERSE");
        break;

      case 'A':  // Turn Left
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH);  analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);   analogWrite(ENB, 200);
        Serial.println("↖ TURN LEFT");
        break;

      case 'D':  // Turn Right
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);   analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH);  analogWrite(ENB, 200);
        Serial.println("↗ TURN RIGHT");
        break;

      case 'F':  // Brake/Stop
        digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);   analogWrite(ENA, 0);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);   analogWrite(ENB, 0);
        Serial.println("■ BRAKE");
        break;

      default:
        // unknown command: treat as brake
        digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);   analogWrite(ENA, 0);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);   analogWrite(ENB, 0);
        Serial.println("■ IDLE");
        break;
    }

  } else {
    // No key pressed: idle/brake
    digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);   analogWrite(ENA, 0);
    digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);   analogWrite(ENB, 0);
    // (optional) Serial.println("Idle");
  }
}
