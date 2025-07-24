// ===== LIBRARIES =====
#include <Wire.h>
#include <BH1750.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_BMP280.h>
#include <TinyGPS++.h>
#include <Servo.h>
#include <SPI.h>
#include <RF24.h>

// ===== MOTOR DEFINITIONS =====
const int IN1 = 8, IN2 = 9, ENA = 10;
const int IN3 = 6, IN4 = 7, ENB = 5;

// ===== RF24 SETUP =====
#define CE_PIN 9
#define CSN_PIN 10
RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";

// ===== SENSOR DEFINITIONS =====
BH1750 lightMeter;
Adafruit_BNO055 bno(55, 0x28, &Wire);
Adafruit_BMP280 bmp;
#define BMP280_I2C_ADDRESS 0x76
TinyGPSPlus gps;
#define GPS_BAUD 9600
#define MQ2_PIN A1

// ===== SERVOS =====
Servo servo1, servo2, servo3;
int angle1 = 90, angle2 = 90, angle3 = 90;

// ===== TIMING =====
unsigned long lastSensorPrint = 0;

void setup() {
  Serial.begin(9600);
  Serial1.begin(GPS_BAUD);
  Wire.begin();
  delay(100);

  // Motor pins
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Servo setup
  servo1.attach(2);
  servo2.attach(3);
  servo3.attach(4);
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  // Sensor init
  lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);
  bmp.setSampling(
    Adafruit_BMP280::MODE_NORMAL,
    Adafruit_BMP280::SAMPLING_X2,
    Adafruit_BMP280::SAMPLING_X16,
    Adafruit_BMP280::FILTER_X16,
    Adafruit_BMP280::STANDBY_MS_500
  );
  pinMode(MQ2_PIN, INPUT);

  // RF24 init
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_1MBPS);
  radio.openReadingPipe(0, address);
  radio.startListening();

  Serial.println(F("RF Rover Ready: use WASD, F, o/p/k/l/n/m"));
}

void loop() {
  // === RECEIVE RF COMMAND ===
  char c;
  if (radio.available()) {
    radio.read(&c, sizeof(c));
    Serial.print("Cmd: ");
    Serial.println(c);

    switch (c) {
      case 'W': case 'w':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB, 200);
        Serial.println(F("-> FORWARD")); break;
      case 'S': case 's':
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB, 200);
        Serial.println(F("<- REVERSE")); break;
      case 'A': case 'a':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA,200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB,200);
        Serial.println(F("<< LEFT")); break;
      case 'D': case 'd':
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA,200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB,200);
        Serial.println(F(">> RIGHT")); break;
      case 'F': case 'f':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);  analogWrite(ENA, 0);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);  analogWrite(ENB, 0);
        Serial.println(F("[BRAKE]")); break;

      // Servo 1 (o/p)
      case 'o': angle1 = constrain(angle1 - 5, 0, 270); servo1.write(angle1); Serial.print(F("S1:")); Serial.println(angle1); break;
      case 'p': angle1 = constrain(angle1 + 5, 0, 270); servo1.write(angle1); Serial.print(F("S1:")); Serial.println(angle1); break;

      // Servo 2 (k/l)
      case 'k': angle2 = constrain(angle2 - 5, 0, 180); servo2.write(angle2); Serial.print(F("S2:")); Serial.println(angle2); break;
      case 'l': angle2 = constrain(angle2 + 5, 0, 180); servo2.write(angle2); Serial.print(F("S2:")); Serial.println(angle2); break;

      // Servo 3 (n/m)
      case 'n': angle3 = constrain(angle3 - 5, 0, 180); servo3.write(angle3); Serial.print(F("S3:")); Serial.println(angle3); break;
      case 'm': angle3 = constrain(angle3 + 5, 0, 180); servo3.write(angle3); Serial.print(F("S3:")); Serial.println(angle3); break;

      default: break;
    }
  }

  // === SENSORS TELEMETRY (1Hz) ===
  if (millis() - lastSensorPrint > 1000) {
    lastSensorPrint = millis();

    while (Serial1.available()) gps.encode(Serial1.read());
    String gpsS = gps.location.isValid()
      ? "Lat=" + String(gps.location.lat(), 6) + ";Lon=" + String(gps.location.lng(), 6)
      : "WaitingForFix";

    float lux = lightMeter.readLightLevel();

    sensors_event_t e;
    bno.getEvent(&e, Adafruit_BNO055::VECTOR_EULER);
    String ori = String(e.orientation.x, 2) + "/" + String(e.orientation.y, 2) + "/" + String(e.orientation.z, 2);

    float temp = bmp.readTemperature();
    float pres = bmp.readPressure() / 100.0F;

    int raw = analogRead(MQ2_PIN);
    float v = raw * (5.0 / 1023.0);

    Serial.print(F("GPS:"));     Serial.print(gpsS);
    Serial.print(F(",LIGHT:"));  Serial.print(lux, 2);
    Serial.print(F(",ORI:"));    Serial.print(ori);
    Serial.print(F(",BMP:T="));  Serial.print(temp, 2);
    Serial.print(F(";P="));      Serial.print(pres, 2);
    Serial.print(F(",MQ2_RAW:"));Serial.print(raw);
    Serial.print(F(",MQ2_V:"));  Serial.println(v, 2);
  }
}
