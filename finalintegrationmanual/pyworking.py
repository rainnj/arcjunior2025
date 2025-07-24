import serial
import time
import pygame

# Replace with your actual port (e.g., COM3, COM12, etc.)
SERIAL_PORT = '/dev/ttyACM0'
BAUD_RATE = 9600

# Connect to Arduino
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # wait for Arduino to reset
    print(f"[] Connected to Arduino on {SERIAL_PORT}")
except Exception as e:
    print("[] Failed to connect:", e)
    exit()

# Setup pygame
pygame.init()
screen = pygame.display.set_mode((300, 200))
pygame.display.set_caption("WASD Motor Control")

running = True
last_sent = None

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_w] and last_sent != 'W':
        ser.write(b'W')
        last_sent = 'W'
        print("W")

    elif keys[pygame.K_s] and last_sent != 'S':
        ser.write(b'S')
        last_sent = 'S'
        print("S → Reverse")

    elif keys[pygame.K_a] and last_sent != 'A':
        ser.write(b'A')
        last_sent = 'A'
        print("A → Left")

    elif keys[pygame.K_d] and last_sent != 'D':
        ser.write(b'D')
        last_sent = 'D'
        print("D → Right")

    elif keys[pygame.K_f] and last_sent != 'F':
        ser.write(b'F')
        last_sent = 'F'
        print("F → Brake")

    elif not any([keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_f]]):
        if last_sent != 'X':
            ser.write(b'F')  # idle fallback
            last_sent = 'X'

    pygame.time.delay(100)

ser.close()
pygame.quit()
