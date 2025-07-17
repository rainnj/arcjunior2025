import pygame
import time
import sys

# Initialize pygame and joystick
pygame.init()
pygame.joystick.init()

# Default control values
lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
controller_connected = False
keyboard_active = False

# Try to initialize controller
if pygame.joystick.get_count() > 0:
    try:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        controller_connected = True
        print("🎮 Controller connected:", joystick.get_name())
        print("🔁 Reading both sticks (left + right)...")
    except:
        controller_connected = False

if not controller_connected:
    print("❌ No controller detected. Falling back to WASD keyboard controls.")
    print("Usage: W/S for forward/backward, A/D for left/right")
    print("Hold Shift for right stick emulation (camera control)")
    keyboard_active = True

try:
    while True:
        pygame.event.pump()  # Process event queue
        
        # Reset values each frame
        lx, ly, rx, ry = 0.0, 0.0, 0.0, 0.0
        
        if controller_connected:
            # Check if controller got disconnected
            if pygame.joystick.get_count() == 0:
                controller_connected = False
                keyboard_active = True
                print("⚠️ Controller disconnected! Falling back to WASD keyboard controls.")
            
            # Read controller axes if still connected
            if controller_connected:
                lx = joystick.get_axis(0)
                ly = joystick.get_axis(1)
                rx = joystick.get_axis(2)
                ry = joystick.get_axis(3)
        
        if keyboard_active:
            # Check if controller got reconnected
            if pygame.joystick.get_count() > 0 and not controller_connected:
                try:
                    joystick = pygame.joystick.Joystick(0)
                    joystick.init()
                    controller_connected = True
                    keyboard_active = False
                    print("🎮 Controller reconnected! Switching back to controller input.")
                except:
                    pass
            
            # Read keyboard inputs if no controller
            if keyboard_active:
                keys = pygame.key.get_pressed()
                
                # Left stick emulation (movement)
                if keys[pygame.K_w]: ly = -1.0
                if keys[pygame.K_s]: ly = 1.0
                if keys[pygame.K_a]: lx = -1.0
                if keys[pygame.K_d]: lx = 1.0
                
                # Right stick emulation (hold Shift + WASD)
                if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                    if keys[pygame.K_w]: ry = -1.0
                    if keys[pygame.K_s]: ry = 1.0
                    if keys[pygame.K_a]: rx = -1.0
                    if keys[pygame.K_d]: rx = 1.0
        
        # Print the current control values
        print(f"🕹️  Left Stick: X={lx:.2f}  Y={ly:.2f}    |    Right Stick: X={rx:.2f}  Y={ry:.2f}", end='\r')
        
        # Small delay to prevent high CPU usage
        time.sleep(0.05)

except KeyboardInterrupt:
    print("\n🛑 Stopped.")
    pygame.quit()
    sys.exit()
