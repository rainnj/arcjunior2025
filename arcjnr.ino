#include <Wire.h>
#include <SPI.h>
#include <RF24.h>
#include <BH1750.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_BMP280.h>
#include <TinyGPS++.h>
#include <Servo.h>

// ========== MOTOR & RF DEFINITIONS ========== //
const int IN1 = 6, IN2 = 7, ENA = 5;
const int IN3 = 8, IN4 = 9, ENB = 10;

// nRF24L01+ CE/CS pins
#define CE_PIN   11
#define CSN_PIN  12
RF24 radio(CE_PIN, CSN_PIN);
// Two fixed 5‑byte addresses; swapped on the base station sketch
const uint64_t PIPE_TX = 0xF0F0F0F0A1LL;
const uint64_t PIPE_RX = 0xF0F0F0B1A1LL;

// ========== SENSORS ========== //
BH1750              lightMeter;
Adafruit_BNO055     bno(55, 0x28, &Wire);
Adafruit_BMP280     bmp;
#define BMP280_I2C_ADDRESS 0x76
TinyGPSPlus         gps;
#define GPS_BAUD      9600
#define MQ2_PIN       A1

// ========== SERVOS ========== //
Servo servo1, servo2, servo3;
int angle1 = 90, angle2 = 90, angle3 = 90;

// Timing
unsigned long lastSensorPrint = 0;

void setup() {
  // --- Serials ---
  Serial.begin(9600);
  Serial1.begin(GPS_BAUD);
  Wire.begin();
  delay(100);

  // --- RF24 init ---
  if (!radio.begin()) {
    Serial.println(F("RF24 init failed"));
    while (1);
  }
  radio.setDataRate(RF24_1MBPS);
  radio.setPALevel(RF24_PA_LOW);
  radio.openWritingPipe(PIPE_TX);
  radio.openReadingPipe(1, PIPE_RX);
  radio.startListening();


  // --- Motor & servo pins ---
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  servo1.attach(2);
  servo2.attach(3);
  servo3.attach(4);
  servo1.write(angle1);
  servo2.write(angle2);
  servo3.write(angle3);

  // --- Sensors init ---
  lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE);

  bmp.setSampling(
    Adafruit_BMP280::MODE_NORMAL,
    Adafruit_BMP280::SAMPLING_X2,
    Adafruit_BMP280::SAMPLING_X16,
    Adafruit_BMP280::FILTER_X16,
    Adafruit_BMP280::STANDBY_MS_500
  );

  pinMode(MQ2_PIN, INPUT);

  Serial.println(F("Setup done. W/A/S/D=drive, F=brake"));
  Serial.println(F("o/p=servo1, k/l=servo2, n/m=servo3"));
}

void loop() {
  // --- 1) Forward Serial (USB) → RF ---
  if (Serial.available()) {
    size_t len = Serial.available();
    if (len > 32) len = 32;
    char buf[32] = {0};
    Serial.readBytes(buf, len);
    radio.stopListening();
    radio.write(buf, 32);
    radio.startListening();
  }

  // --- 2) Forward RF → Serial (USB) ---
  if (radio.available()) {
    char buf[32] = {0};
    radio.read(buf, 32);
    Serial.write(buf, 32);
  }

  // --- 3) Command handling from Serial ---
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') return;
     handleCommand(c);
  }
    Serial.print(F("Cmd: "));
    Serial.println(c);
    switch (c) {
      case 'W': case 'w':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA, 200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB, 200);
        Serial.println(F("→ FORWARD")); break;
      case 'S': case 's':
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA, 200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB, 200);
        Serial.println(F("← REVERSE")); break;
      case 'A': case 'a':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, HIGH); analogWrite(ENA,200);
        digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);  analogWrite(ENB,200);
        Serial.println(F("↖ TURN LEFT")); break;
      case 'D': case 'd':
        digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);  analogWrite(ENA,200);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, HIGH); analogWrite(ENB,200);
        Serial.println(F("↗ TURN RIGHT")); break;
      case 'F': case 'f':
        digitalWrite(IN1, LOW);  digitalWrite(IN2, LOW);  analogWrite(ENA,0);
        digitalWrite(IN3, LOW);  digitalWrite(IN4, LOW);  analogWrite(ENB,0);
        Serial.println(F("■ BRAKE")); break;
  // SERVO 1 ↓/↑ (keys: o/p)
  case 'o':  // decrement S1
    angle1 = constrain(angle1 - 5, 0, 270);
    servo1.write(angle1);
    Serial.print(F("S1:")); Serial.println(angle1);
    break;
  case 'p':  // increment S1
    angle1 = constrain(angle1 + 5, 0, 270);
    servo1.write(angle1);
    Serial.print(F("S1:")); Serial.println(angle1);
    break;

  // SERVO 2 ↓/↑ (keys: k/l)
  case 'k':  // decrement S2
    angle2 = constrain(angle2 - 5, 0, 180);
    servo2.write(angle2);
    Serial.print(F("S2:")); Serial.println(angle2);
    break;
  case 'l':  // increment S2
    angle2 = constrain(angle2 + 5, 0, 180);
    servo2.write(angle2);
    Serial.print(F("S2:")); Serial.println(angle2);
    break;

  // SERVO 3 ↓/↑ (keys: n/m)
  case 'n':  // decrement S3
    angle3 = constrain(angle3 - 5, 0, 180);
    servo3.write(angle3);
    Serial.print(F("S3:")); Serial.println(angle3);
    break;
  case 'm':  // increment S3
    angle3 = constrain(angle3 + 5, 0, 180);
    servo3.write(angle3);
    Serial.print(F("S3:")); Serial.println(angle3);
    break;

  default:
    // any other commands…
    break;
}
  }
  // --- 4) Telemetry @ 1 Hz ---
  if (millis() - lastSensorPrint > 1000) {
    lastSensorPrint = millis();

    // GPS
    while (Serial1.available()) gps.encode(Serial1.read());
    String gpsS = gps.location.isValid()
      ? "Lat=" + String(gps.location.lat(), 6) +
        ";Lon=" + String(gps.location.lng(), 6)
      : "WaitingForFix";

    // Light
    float lux = lightMeter.readLightLevel();

    // IMU orientation
    sensors_event_t e;
    bno.getEvent(&e, Adafruit_BNO055::VECTOR_EULER);
    String ori = String(e.orientation.x,2) + "/" +
                 String(e.orientation.y,2) + "/" +
                 String(e.orientation.z,2);

    // BMP280
    float temp = bmp.readTemperature();
    float pres = bmp.readPressure() / 100.0F;

    // MQ2
    int raw = analogRead(MQ2_PIN);
    float v   = raw * (5.0 / 1023.0);

    // Print the telemetry
    Serial.print(F("GPS:"));     Serial.print(gpsS);
    Serial.print(F(",LIGHT:"));  Serial.print(lux, 2);
    pp

    Serial.print(F(",ORI:"));    Serial.print(ori);
    Serial.print(F(",BMP:"));    Serial.print(F("T=")); Serial.print(temp,2);
                                 Serial.print(F(";P=")); Serial.print(pres,2);
    Serial.print(F(",MQ2_RAW:"));Serial.print(raw);
    Serial.print(F(",MQ2_V:"));  Serial.println(v,2);
  }
}
