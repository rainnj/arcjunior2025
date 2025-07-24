// Motor Pins (no conflict)
const int IN1 = 6;    // Left motor dir A1
const int IN2 = 7;    // Left motor dir A2
const int ENA = 5;    // Left motor speed (PWM)
const int IN3 = 8;    // Right motor dir B1
const int IN4 = 4;    // Right motor dir B2 (CHANGED from 9 to 4)
const int ENB = 3;    // Right motor speed (PWM) (CHANGED from 10 to 3)

void setup() {
  Serial.begin(9600);
  delay(100);
  Serial.println("🚗 Rover Ready (USB Mode)");

  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    cmd = toupper(cmd);

    switch (cmd) {
      case 'W':  // Forward
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB, 200);
        Serial.println("↑ FORWARD");
        break;

      case 'S':  // Backward
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB, 200);
        Serial.println("↓ REVERSE");
        break;

      case 'A':  // Turn Left
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB, 200);
        Serial.println("← LEFT");
        break;

      case 'D':  // Turn Right
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB, 200);
        Serial.println("→ RIGHT");
        break;

      case 'F':  // Stop
      default:
        digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);  analogWrite(ENA, 0);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);  analogWrite(ENB, 0);
        Serial.println("■ STOP");
        break;
    }
  }
}
