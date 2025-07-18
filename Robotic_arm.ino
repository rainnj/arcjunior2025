#include <Servo.h>

Servo servo1;
Servo servo2;
Servo servo3;

int angle1 = 90;  // Start at neutral
int angle2 = 90;
int angle3 = 90;

void setup() {
  Serial.begin(9600);

  servo1.attach(9);
  servo2.attach(10);
  servo3.attach(11);

  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  Serial.println("Use keys Q/W for servo1, A/S for servo2, Z/X for servo3.");
}

void loop() {
  if (Serial.available()) {
    char input = Serial.read();

    switch (input) {
      case 'q': angle1 = constrain(angle1 + 5, 0, 180); break;
      case 'w': angle1 = constrain(angle1 - 5, 0, 180); break;
      case 'a': angle2 = constrain(angle2 + 5, 0, 180); break;
      case 's': angle2 = constrain(angle2 - 5, 0, 180); break;
      case 'z': angle3 = constrain(angle3 + 5, 0, 180); break;
      case 'x': angle3 = constrain(angle3 - 5, 0, 180); break;
    }

    servo1.write(angle1);
    servo2.write(angle2);
    servo3.write(angle3);

    Serial.print("Angles: ");
    Serial.print(angle1); Serial.print(" ");
    Serial.print(angle2); Serial.print(" ");
    Serial.println(angle3);
  }
}
