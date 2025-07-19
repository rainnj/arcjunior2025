#include <SPI.h>
#include <Wire.h>
#include <RF24.h>
#include <Servo.h>
#include <BH1750.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_BNO055.h>
#include <Adafruit_BME680.h>
#include <TinyGPS++.h>

// ========== PINS & GLOBALS ========== //
#define CE_PIN 9
#define CSN_PIN 10
#define MQ2_PIN A0
#define RXPin 0
#define TXPin 1
#define GPSBaud 9600
#define BME680_ADDR 0x77

const int IN1 = 2, IN2 = 3, ENA = 5;
const int IN3 = 4, IN4 = 7, ENB = 6;
int speedVal = 200;

Servo servo1, servo2, servo3;
int angle1 = 90, angle2 = 90, angle3 = 90;

// ========== RF ========== //
RF24 radio(CE_PIN, CSN_PIN);
const uint64_t pipes[2] = { 0xF0F0F0F0D2LL, 0xF0F0F0F0E1LL };
char rfBuffer[128];

// ========== SENSOR OBJECTS ========== //
BH1750 lightMeter;
Adafruit_BNO055 bno = Adafruit_BNO055(55, 0x28, &Wire);
Adafruit_BME680 bme;
TinyGPSPlus gps;

// ========== ENUM ========== //
enum Command {
  CMD_FORWARD, CMD_REVERSE, CMD_LEFT, CMD_RIGHT,
  CMD_STOP, CMD_COAST, CMD_SPEED_UP, CMD_SPEED_DOWN, CMD_NONE
};

// ========== SETUP ========== //
void setup() {
  Serial.begin(115200);
  Serial1.begin(GPSBaud);
  Wire.begin();

  pinMode(IN1, OUTPUT); pinMode(IN2, OUTPUT); pinMode(ENA, OUTPUT);
  pinMode(IN3, OUTPUT); pinMode(IN4, OUTPUT); pinMode(ENB, OUTPUT);
  servo1.attach(8); servo2.attach(12); servo3.attach(13);
  servo1.write(angle1); servo2.write(angle2); servo3.write(angle3);
  pinMode(MQ2_PIN, INPUT);

  if (lightMeter.begin(BH1750::CONTINUOUS_HIGH_RES_MODE)) Serial.println(F("BH1750 initialized"));
  else Serial.println(F("BH1750 failed"));

  if (!bno.begin()) { Serial.println("BNO055 not found"); while (1); }
  if (!bme.begin(BME680_ADDR)) { Serial.println("BME680 not found"); while (1); }

  bme.setTemperatureOversampling(BME680_OS_8X);
  bme.setHumidityOversampling(BME680_OS_2X);
  bme.setPressureOversampling(BME680_OS_4X);
  bme.setIIRFilterSize(BME680_FILTER_SIZE_3);
  bme.setGasHeater(320, 150);

  if (!radio.begin()) { Serial.println("RF24 error"); while (1); }
  radio.setPALevel(RF24_PA_LOW);
  radio.setChannel(76);
  radio.setDataRate(RF24_250KBPS);
  radio.enableDynamicPayloads();
  radio.setRetries(5, 15);
  radio.openWritingPipe(pipes[1]);
  radio.openReadingPipe(1, pipes[0]);
  radio.startListening();

  Serial.println("System ready");
  brake();
}

// ========== LOOP ========== //
void loop() {
  if (Serial.available()) {
    char input = tolower(Serial.read());
    if (isMotorCommand(input)) executeMotorCommand(decodeMotorCommand(input));
    else updateServoAngles(input);
    sendTelemetry();
  }

  while (Serial1.available() > 0) {
    if (gps.encode(Serial1.read())) displayGPS();
  }

  if (millis() > 5000 && gps.charsProcessed() < 10) Serial.println("GPS not detected!");

  displayLight();
  displayIMU();
  displayBME680();
  displayMQ2();
  delay(1000);

  // Receive RF data
  if (radio.available()) {
    char incoming[128];
    radio.read(&incoming, sizeof(incoming));
    Serial.print("Received: ");
    Serial.println(incoming);
  }
}

// ========== MOTOR CONTROL ========== //
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
      Serial.println("FORWARD"); break;
    case CMD_REVERSE:
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("REVERSE"); break;
    case CMD_LEFT:
      digitalWrite(IN1, LOW); digitalWrite(IN2, HIGH);
      digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("LEFT"); break;
    case CMD_RIGHT:
      digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW); digitalWrite(IN4, HIGH);
      analogWrite(ENA, speedVal); analogWrite(ENB, speedVal);
      Serial.println("RIGHT"); break;
    case CMD_STOP: brake(); Serial.println("BRAKE"); break;
    case CMD_COAST:
      digitalWrite(IN1, LOW); digitalWrite(IN2, LOW);
      digitalWrite(IN3, LOW); digitalWrite(IN4, LOW);
      analogWrite(ENA, 0); analogWrite(ENB, 0);
      Serial.println("COAST"); break;
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

// ========== SERVO CONTROL ========== //
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
  Serial.print("Servo Angles: ");
  Serial.print(angle1); Serial.print(", ");
  Serial.print(angle2); Serial.print(", ");
  Serial.println(angle3);
}

// ========== TELEMETRY ========== //
void sendTelemetry() {
  float lux = lightMeter.readLightLevel();
  bme.performReading();
  int raw = analogRead(MQ2_PIN);
  float ppm_CH4 = raw * 0.5;
  float ppm_LPG = raw * 0.6;

  float lat = gps.location.isValid() ? gps.location.lat() : 0.0;
  float lng = gps.location.isValid() ? gps.location.lng() : 0.0;

  snprintf(rfBuffer, sizeof(rfBuffer),
    "T:%.1fC H:%.1f%% P:%.0fhPa G:%.1fk CH4~%.0f LPG~%.0f Lux:%.0f Lat:%.2f Lon:%.2f",
    bme.temperature,
    bme.humidity,
    bme.pressure / 100.0,
    bme.gas_resistance / 1000.0,
    ppm_CH4,
    ppm_LPG,
    lux,
    lat,
    lng
  );

  radio.stopListening();
  bool success = radio.write(&rfBuffer, strlen(rfBuffer) + 1);
  radio.startListening();

  Serial.println(success ? "RF Telemetry Sent:" : "Telemetry send failed.");
  Serial.println(rfBuffer);
}

// ========== SENSOR DISPLAY ========== //
void displayLight() {
  float lux = lightMeter.readLightLevel();
  Serial.println("\n=== LIGHT ===");
  Serial.print("Light: "); Serial.print(lux); Serial.println(" lx");
}

void displayIMU() {
  sensors_event_t orientation, gyro, accel;
  bno.getEvent(&orientation, Adafruit_BNO055::VECTOR_EULER);
  bno.getEvent(&gyro, Adafruit_BNO055::VECTOR_GYROSCOPE);
  bno.getEvent(&accel, Adafruit_BNO055::VECTOR_ACCELEROMETER);

  Serial.println("\n=== IMU ===");
  printSensor("Orientation", orientation.orientation.x, orientation.orientation.y, orientation.orientation.z, "deg");
  printSensor("Gyro", gyro.gyro.x, gyro.gyro.y, gyro.gyro.z, "rad/s");
  printSensor("Accel", accel.acceleration.x, accel.acceleration.y, accel.acceleration.z, "m/s²");
}

void displayBME680() {
  if (!bme.performReading()) { Serial.println("BME680 failed!"); return; }
  Serial.println("\n=== ENVIRONMENT ===");
  Serial.print("Temp: "); Serial.print(bme.temperature); Serial.println(" °C");
  Serial.print("Humidity: "); Serial.print(bme.humidity); Serial.println(" %");
  Serial.print("Pressure: "); Serial.print(bme.pressure / 100.0); Serial.println(" hPa");
  Serial.print("Gas: "); Serial.print(bme.gas_resistance / 1000.0); Serial.println(" KΩ");
  Serial.print("Altitude: "); Serial.print(bme.readAltitude(1013.25)); Serial.println(" m");
}

void displayMQ2() {
  int raw = analogRead(MQ2_PIN);
  float voltage = raw * (5.0 / 1023.0);
  float ppm_LPG = raw * 0.6;
  float ppm_CH4 = raw * 0.5;
  float ppm_H2 = raw * 0.4;
  float ppm_Smoke = raw * 0.7;
  float ppm_Alcohol = raw * 0.3;

  Serial.println("\n=== MQ-2 GAS ===");
  Serial.print("Raw: "); Serial.print(raw);
  Serial.print(" | Voltage: "); Serial.print(voltage); Serial.println(" V");
  Serial.print("LPG~: "); Serial.print(ppm_LPG); Serial.print(" ppm");
  Serial.print(" | CH4~: "); Serial.print(ppm_CH4);
  Serial.print(" | H2~: "); Serial.print(ppm_H2);
  Serial.print(" | Smoke~: "); Serial.print(ppm_Smoke);
  Serial.print(" | Alcohol~: "); Serial.println(ppm_Alcohol);
}

void displayGPS() {
  Serial.println("\n=== GPS ===");
  if (gps.location.isValid()) {
    Serial.print("Lat: "); Serial.print(gps.location.lat(), 6);
    Serial.print(", Lon: "); Serial.println(gps.location.lng(), 6);
    Serial.print("Speed: "); Serial.print(gps.speed.kmph()); Serial.println(" km/h");
    Serial.print("Altitude: "); Serial.print(gps.altitude.meters()); Serial.println(" m");
  } else {
    Serial.println("Waiting for GPS fix...");
  }
}

void printSensor(const char* type, float x, float y, float z, const char* unit) {
  Serial.print(type); Serial.print(": X="); Serial.print(x);
  Serial.print(" Y="); Serial.print(y);
  Serial.print(" Z="); Serial.print(z);
  Serial.print(" "); Serial.println(unit);
}
