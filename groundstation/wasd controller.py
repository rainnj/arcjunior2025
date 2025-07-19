import pygame
import time
import sys
# import serial  # Disable for testing without hardware

# === SERIAL SETUP (DISABLED) ===
# try:
#     ser = serial.Serial('COM3', 115200, timeout=1)
#     time.sleep(2)
#     print("✅ Serial connection established with transmitter module.")
# except serial.SerialException as e:
#     print(f"❌ Could not connect to serial port: {e}")
#     sys.exit()

# === PYGAME SETUP ===
pygame.init()
screen = pygame.display.set_mode((200, 100))
pygame.display.set_caption("WASD Rover Controller (Test Mode)")

print("🚗 Test mode: Press W, A, S, or D to simulate rover movement.")
print("Release all keys to simulate 'Stop'.")

last_command = None

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # ser.write(b'S\n')  # Skip serial
                pygame.quit()
                # ser.close()
                sys.exit()

        keys = pygame.key.get_pressed()

        command = None
        if keys[pygame.K_w]:
            command = 'W'
        elif keys[pygame.K_s]:
            command = 'S'
        elif keys[pygame.K_a]:
            command = 'A'
        elif keys[pygame.K_d]:
            command = 'D'
        else:
            command = 'X'  # Idle / Stop

        if command != last_command:
            # Simulate output instead of sending serial
            print(f"📤 Simulated Command: {command}       ", end='\r')
            last_command = command

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
    # ser.write(b'X\n')  # Skip serial
    # ser.close()
    pygame.quit()
    sys.exit()
