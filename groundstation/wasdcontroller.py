import pygame
import time
import sys
import serial

# === SERIAL SETUP ===
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Adjust port if needed
    time.sleep(2)  # Allow time for Arduino to reset
    print(" Serial connection established with Arduino.")
except serial.SerialException as e:
    print(f" Could not connect to serial port: {e}")
    sys.exit()

# === PYGAME SETUP ===
pygame.init()
screen = pygame.display.set_mode((300, 100))
pygame.display.set_caption("WASD + F Rover Controller")

font = pygame.font.SysFont(None, 24)
clock = pygame.time.Clock()

print("🔧 Control: W/A/S/D = Move, F = Brake")

last_command = None

def send_command(cmd):
    global last_command
    if cmd != last_command:
        ser.write(cmd.encode())  # Send as byte
        print(f"📤 Sent Command: {cmd}       ", end='\r')
        last_command = cmd

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                send_command('F')  # Brake before exiting
                ser.close()
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            send_command('W')
        elif keys[pygame.K_s]:
            send_command('S')
        elif keys[pygame.K_a]:
            send_command('A')
        elif keys[pygame.K_d]:
            send_command('D')
        elif keys[pygame.K_f]:
            send_command('F')
        else:
            send_command('F')  # Default to Brake when no key is pressed

        screen.fill((30, 30, 30))
        text = font.render(f"Last Cmd: {last_command or 'None'}", True, (255, 255, 255))
        screen.blit(text, (10, 40))

        pygame.display.flip()
        clock.tick(20)  # Limit loop to 20 FPS

except KeyboardInterrupt:
    print("\n Interrupted. Sending brake command.")
    send_command('F')
    ser.close()
    pygame.quit()
    sys.exit()
