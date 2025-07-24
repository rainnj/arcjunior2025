#include <SPI.h>
#include <RF24.h>

#define CE_PIN 9
#define CSN_PIN 10
RF24 radio(CE_PIN, CSN_PIN);
const byte address[6] = "00001";

void setup() {
  Serial.begin(9600);
  radio.begin();
  radio.setPALevel(RF24_PA_LOW);
  radio.setDataRate(RF24_1MBPS);
  radio.openWritingPipe(address);
  radio.stopListening();
  Serial.println("🚀 Ground Station Ready. Type WASD, F, o/p/k/l/n/m");
}

void loop() {
  if (Serial.available()) {
    char cmd = Serial.read();
    radio.write(&cmd, sizeof(cmd));
    Serial.print("Sent: ");
    Serial.println(cmd);
  }
}
