import time
import sys
import serial
import os

# Add navigation path
sys.path.append('./navigation')

# Import navigation modules
from distance_bearing import haversine, calculate_bearing
from headinglogic import decide_movement

# Import motor control (assuming you'll create this)
try:
    from motor_control import RoverMotorController, execute_movement
    MOTORS_AVAILABLE = True
except ImportError:
    print("[WARNING] Motor control not available - simulation mode only")
    MOTORS_AVAILABLE = False

class RoverNavigator:
    def __init__(self, motor_enabled=True):
        self.motor_controller = None
        self.serial_connection = None
        self.motor_enabled = motor_enabled and MOTORS_AVAILABLE
        
        if self.motor_enabled:
            try:
                self.motor_controller = RoverMotorController()
                print("✅ Motor controller initialized")
            except Exception as e:
                print(f"[WARNING] Could not initialize motors: {e}")
                self.motor_enabled = False

    def load_gps_waypoints(self, filename):
        """Load GPS waypoints from file with better error handling"""
        waypoints = []
        
        # Check if file exists
        if not os.path.exists(filename):
            print(f"[ERROR] Waypoint file not found: {filename}")
            return waypoints
            
        try:
            with open(filename, 'r') as file:
                for line_num, line in enumerate(file, 1):
                    line = line.strip()
                    if not line or line.startswith('#'):  # Skip empty lines and comments
                        continue
                    
                    if ',' not in line:
                        print(f"[WARNING] Line {line_num}: Missing comma - {line}")
                        continue
                        
                    try:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            lat, lon = float(parts[0]), float(parts[1])
                            waypoints.append((lat, lon))
                        else:
                            print(f"[WARNING] Line {line_num}: Insufficient coordinates - {line}")
                    except ValueError as e:
                        print(f"[WARNING] Line {line_num}: Invalid coordinates - {line} ({e})")
                        
        except Exception as e:
            print(f"[ERROR] Could not read waypoint file: {e}")
            
        print(f"✅ Loaded {len(waypoints)} waypoints from {filename}")
        return waypoints

    def parse_nmea_gpgga(self, nmea_sentence):
        """Parse NMEA GPGGA sentence"""
        if not nmea_sentence.startswith("$GPGGA"):
            return None
            
        parts = nmea_sentence.split(",")
        if len(parts) < 6 or parts[2] == '' or parts[4] == '':
            return None
        
        def convert_to_decimal(coord, direction):
            if len(coord) < 4:
                return None
            try:
                degrees = int(coord[:2])
                minutes = float(coord[2:])
                decimal = degrees + minutes / 60
                if direction in ['S', 'W']:
                    decimal *= -1
                return decimal
            except (ValueError, IndexError):
                return None
        
        try:
            lat = convert_to_decimal(parts[2], parts[3])
            lon = convert_to_decimal(parts[4], parts[5])
            if lat is None or lon is None:
                return None
            return lat, lon
        except Exception:
            return None

    def get_current_position_serial(self, timeout=10):
        """Get current position from serial GPS"""
        if not self.serial_connection:
            return None
            
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                line = self.serial_connection.readline().decode(errors='ignore').strip()
                result = self.parse_nmea_gpgga(line)
                if result:
                    return result
            except Exception as e:
                print(f"[WARNING] GPS reading error: {e}")
                continue
                
        print("[WARNING] GPS timeout - no valid position received")
        return None

    def connect_gps_serial(self, port="COM8", baud_rate=9600):
        """Connect to GPS via serial"""
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            print(f"✅ Connected to GPS on {port} at {baud_rate} baud")
            return True
        except Exception as e:
            print(f"[ERROR] Could not open serial port: {e}")
            return False

    def execute_navigation_decision(self, decision):
        """Execute navigation decision"""
        if self.motor_enabled and self.motor_controller:
            execute_movement(decision, self.motor_controller)
        else:
            print(f"[SIMULATION] Would execute: {decision.upper()}")

    def run_simulation(self, simulated_positions_file, waypoints_file):
        """Run navigation simulation"""
        print("🚀 Starting Simulation Mode...\n")
        
        simulated_positions = self.load_gps_waypoints(simulated_positions_file)
        target_waypoints = self.load_gps_waypoints(waypoints_file)
        
        if not simulated_positions or not target_waypoints:
            print("❌ Could not load required files for simulation")
            return
        
        waypoint_index = 0
        
        for i in range(1, len(simulated_positions)):
            curr_lat, curr_lon = simulated_positions[i]
            prev_lat, prev_lon = simulated_positions[i - 1]
            
            if waypoint_index >= len(target_waypoints):
                print("✅ All waypoints reached!")
                break
            
            target_lat, target_lon = target_waypoints[waypoint_index]
            distance = haversine(curr_lat, curr_lon, target_lat, target_lon)
            current_heading = calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)
            target_bearing = calculate_bearing(curr_lat, curr_lon, target_lat, target_lon)
            decision = decide_movement(current_heading, target_bearing)
            
            print(f"📍 Current: ({curr_lat:.6f}, {curr_lon:.6f})")
            print(f"🎯 Target:  ({target_lat:.6f}, {target_lon:.6f})")
            print(f"📏 Distance: {distance:.2f} m")
            print(f"🧭 Heading:  {current_heading:.2f}°")
            print(f"🧭 Bearing:  {target_bearing:.2f}°")
            print(f"🦾 Action:   {decision.upper()}")
            print("-" * 50)
            
            self.execute_navigation_decision(decision)
            
            if distance < 2.0:
                print(f"✅ Reached waypoint {waypoint_index + 1}/{len(target_waypoints)}")
                waypoint_index += 1
                if self.motor_enabled:
                    time.sleep(2)  # Pause between waypoints
            
            time.sleep(1)

    def run_live_navigation(self, waypoints_file, gps_port="COM8", baud_rate=9600):
        """Run live GPS navigation"""
        print("🛰️ Starting Live GPS Navigation...\n")
        
        # Load waypoints
        waypoints = self.load_gps_waypoints(waypoints_file)
        if not waypoints:
            print("❌ No GPS waypoints loaded.")
            return
        
        # Connect to GPS
        if not self.connect_gps_serial(gps_port, baud_rate):
            return
        
        waypoint_index = 0
        prev_lat, prev_lon = None, None
        gps_fail_count = 0
        max_gps_fails = 5
        
        try:
            while waypoint_index < len(waypoints):
                try:
                    position = self.get_current_position_serial(timeout=5)
                    if position is None:
                        gps_fail_count += 1
                        print(f"[WARNING] GPS read failed ({gps_fail_count}/{max_gps_fails})")
                        if gps_fail_count >= max_gps_fails:
                            print("❌ Too many GPS failures. Stopping rover.")
                            break
                        if self.motor_enabled:
                            self.motor_controller.stop()
                        time.sleep(2)
                        continue
                    
                    gps_fail_count = 0  # Reset on successful read
                    lat, lon = position
                    
                    if prev_lat is None:
                        prev_lat, prev_lon = lat, lon
                        print("⏳ Waiting for movement to calculate heading...")
                        time.sleep(1)
                        continue
                    
                    target_lat, target_lon = waypoints[waypoint_index]
                    distance = haversine(lat, lon, target_lat, target_lon)
                    current_heading = calculate_bearing(prev_lat, prev_lon, lat, lon)
                    target_bearing = calculate_bearing(lat, lon, target_lat, target_lon)
                    decision = decide_movement(current_heading, target_bearing)
                    
                    print(f"📍 Current: ({lat:.6f}, {lon:.6f})")
                    print(f"🎯 Target:  ({target_lat:.6f}, {target_lon:.6f})")
                    print(f"📏 Distance: {distance:.2f} m")
                    print(f"🧭 Heading:  {current_heading:.2f}°")
                    print(f"🧭 Bearing:  {target_bearing:.2f}°")
                    print(f"🦾 Action:   {decision.upper()}")
                    print("-" * 40)
                    
                    self.execute_navigation_decision(decision)
                    
                    if distance < 3.0:  # Slightly relaxed threshold
                        print(f"✅ Reached waypoint {waypoint_index + 1}/{len(waypoints)}\n")
                        waypoint_index += 1
                        if self.motor_enabled:
                            self.motor_controller.stop()
                            time.sleep(2)  # Pause between waypoints
                    
                    prev_lat, prev_lon = lat, lon
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    print("\n🛑 Stopped by user.")
                    break
                except Exception as e:
                    print(f"❌ Unexpected error: {e}")
                    if self.motor_enabled:
                        self.motor_controller.stop()
                    time.sleep(1)
                    continue
                    
        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        if self.motor_controller:
            self.motor_controller.cleanup()
        if self.serial_connection:
            self.serial_connection.close()
        print("🧹 Cleaned up resources.")

def main():
    print("🚀 Rover Navigation System Starting...")
    
    # Create navigator instance
    navigator = RoverNavigator(motor_enabled=True)
    
    # Check command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        # Simulation mode
        navigator.run_simulation(
            'gpslocations/simulated-path.txt',
            'gpslocations/sample-gpslocations.txt'
        )
    else:
        # Live GPS mode
        gps_port = input("Enter GPS port (default: COM8): ").strip() or "COM8"
        navigator.run_live_navigation(
            'gpslocations/sample-gpslocations.txt',
            gps_port=gps_port
        )

if __name__ == "__main__":
    main()
