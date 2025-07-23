#include <SPI.h>
#include <RF24.h>

// Pin definitions
#define CE_PIN 9
#define CSN_PIN 10

// Pipe addresses (Must match on both devices, but reversed!)
const uint64_t pipes[2] = { 0xF0F0F0F0D2LL, 0xF0F0F0F0E1LL };

// Create RF24 radio object
RF24 radio(CE_PIN, CSN_PIN);

// Data structure to transmit
struct TelemetryData {
  float temperature;
  float humidity;
  int tagId;
  uint32_t timestamp;
};

TelemetryData telemetry;

// Buffer for incoming commands
char commandBuffer[64];

void setup() {
  Serial.begin(115200);

  if (!radio.begin()) {
    Serial.println("Radio hardware not responding!");
    while (1);
  }

  radio.setPALevel(RF24_PA_LOW);
  radio.setChannel(76);
  radio.setDataRate(RF24_250KBPS);
  radio.enableDynamicPayloads();
  radio.setRetries(5, 15);

  // Set both pipes
  radio.openWritingPipe(pipes[1]);  // Pipe to write to (other node's reading pipe)
  radio.openReadingPipe(1, pipes[0]); // Pipe to read from (other node's writing pipe)

  radio.startListening();

  Serial.println("Transceiver ready...");
}

void loop() {
  // Check if a command was received
  if (radio.available()) {
    memset(commandBuffer, 0, sizeof(commandBuffer)); // Clear previous command
    radio.read(&commandBuffer, sizeof(commandBuffer));

    Serial.print("Command received: ");
    Serial.println(commandBuffer);

    // Simulate telemetry (or replace with sensor readings)
    telemetry.temperature = 25.0 + random(-50, 50) / 10.0;
    telemetry.humidity = 60.0 + random(-100, 100) / 10.0;
    telemetry.tagId = 1;
    telemetry.timestamp = millis();

    delay(100);  // Simulate processing time

    // Send telemetry back
    radio.stopListening();
    bool success = radio.write(&telemetry, sizeof(telemetry));
    if (success) {
      Serial.println("Telemetry sent.");
    } else {
      Serial.println("Telemetry send failed.");
    }
    radio.startListening();
  }


}
