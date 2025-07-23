#include <SPI.h>
#include <RF24.h>

#define CE_PIN 9
#define CSN_PIN 10

const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL }; // TX, RX pipe

RF24 radio(CE_PIN, CSN_PIN);

// Serial buffer
const int BUFFER_SIZE = 64;
char serialBuffer[BUFFER_SIZE];
int bufferIndex = 0;

// Structure to receive telemetry
struct TelemetryData {
  float temperature;
  float humidity;
  int tagId;
  uint32_t timestamp;
};

TelemetryData telemetry;

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

  radio.openWritingPipe(pipes[1]);  // Send to other node
  radio.openReadingPipe(1, pipes[0]); // Listen for response

  radio.stopListening();  // Start in TX mode
  Serial.println("Transceiver ready.");
}

void loop() {
  while (Serial.available() > 0) {
    char inChar = Serial.read();

    if (inChar == '\n') {
      serialBuffer[bufferIndex] = '\0';
      sendCommand(serialBuffer);
      bufferIndex = 0;
    } else if (bufferIndex < BUFFER_SIZE - 1) {
      serialBuffer[bufferIndex++] = inChar;
    }
  }
}

void sendCommand(const char* command) {
  Serial.print("SENDING: ");
  Serial.println(command);

  radio.stopListening(); // Set to TX
  bool ok = radio.write(command, strlen(command) + 1);

  if (ok) {
    Serial.println("SEND_OK");
  } else {
    Serial.println("SEND_FAIL");
    return;
  }

  // Now wait for telemetry response
  radio.startListening(); // Set to RX

  unsigned long startTime = millis();
  bool timeout = false;

  while (!radio.available()) {
    if (millis() - startTime > 500) { // 500 ms timeout
      timeout = true;
      break;
    }
  }

  if (!timeout) {
    radio.read(&telemetry, sizeof(telemetry));
    Serial.println("TELEMETRY RECEIVED:");
    Serial.print("Temperature: "); Serial.println(telemetry.temperature);
    Serial.print("Humidity: "); Serial.println(telemetry.humidity);
    Serial.print("Tag ID: "); Serial.println(telemetry.tagId);
    Serial.print("Timestamp: "); Serial.println(telemetry.timestamp);
  } else {
    Serial.println("No telemetry received (timeout).");
  }

  radio.stopListening(); // Back to TX mode
}
