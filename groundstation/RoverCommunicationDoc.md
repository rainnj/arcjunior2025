# Arduino Rover Communication

This project implements Task 2 of the Arc Jr project: Communication between an Arduino Uno and a rover using nRF24L01+ radio module.

## Hardware Requirements

- Arduino Uno
- nRF24L01+ radio module
- Connecting wires

## Pin Connections

nRF24L01+ to Arduino Uno:
- CE -> Pin 9
- CSN -> Pin 10
- MOSI -> Pin 11 (SPI)
- MISO -> Pin 12 (SPI)
- SCK -> Pin 13 (SPI)
- VCC -> 3.3V
- GND -> GND

## Software Requirements

1. Arduino IDE (2.x or later)
2. Required Libraries:
   - RF24 library
   - SPI library (included with Arduino IDE)

## Installation

1. Install the RF24 library in Arduino IDE:
   - Tools > Manage Libraries
   - Search for "RF24"
   - Install the library by TMRh20

2. Connect the Arduino Uno to your computer

3. Upload the code:
   - Open `arduino/rover_communication/rover_communication.ino`
   - Select board: Tools > Board > Arduino AVR Boards > Arduino Uno
   - Select port: Tools > Port > (your Arduino port)
   - Click Upload

## Usage

1. Open Serial Monitor (Tools > Serial Monitor)
2. Set baud rate to 115200
3. The system will:
   - Read commands from Serial Monitor and send them to rover
   - Receive telemetry data from rover and display it

### Command Format
- Type any command in Serial Monitor and press Enter
- You'll see confirmation: `CMD_SENT:your_command`

### Telemetry Format
Incoming telemetry appears as:
```
TELEMETRY,temperature,humidity,tagId,timestamp
```
Example: `TELEMETRY,25.5,60.0,123,1234567890`

## Troubleshooting

1. Radio Not Responding:
   - Check nRF24L01+ connections
   - Verify 3.3V power supply
   - Reset Arduino

2. No Serial Communication:
   - Verify correct port selection
   - Check baud rate (115200)
   - Reset Arduino

## Project Structure

```
.
├── arduino/
│   └── rover_communication/
│       └── rover_communication.ino    # Main Arduino code
└── .vscode/                          # VS Code configuration
    ├── arduino.json                  # Arduino settings
    └── c_cpp_properties.json         # C++ configuration
```

## Extra simplified documentation 


# Serial.begin(115200); : the serial is a built in arduino communication object and the 115200 is the baud reate bits per second 
# the const int buffer_size = 64 is saying that we have a box that can hold to 64 letters it saves memory of the command
# the serial buffer is the same but each number is a small box that only holds one character
# the int bufferindex = 0 means that it starts at 0 the first position
# the SetPA level : is to control how strong the radio signal is 
    low is good for testing purposes but we might need to switch 
    to high or mid depending on the distance of the rover

# set Channel is like choosing a radio station 76 is the frequencu
    range is 0-125 both radios must use the same Channel

# Set data rate : how fast data is transmited
    250KBPS = 250 kb per second
    also both radios must use the same rate to Working

# enable dynamic paylods : allows sending different sized messages

# setRetries(a, b) : a = if message fails try n times and then b is
    how many units to wait between setRetries (5,15) are good 


## THE MAIN LOOP 
    this is what is collecting the data from the rover when the serial
    is avaliable and part 2 checks for the data from rover 


## Processing Commands 
    it stops listening so we can send the command to the rover 
    to get the data again and starts listening after


## Sending the telemetry 
    then it prints the telemetry that we got 

