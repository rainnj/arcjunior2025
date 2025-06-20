import serial
import time
from navigation.distance_bearing import haversine, calculate_bearing
from navigation.headinglogic import decide_movement
from motor_control import RoverMotorController, execute_movement  # Import motor control

def load_gps_waypoints(filename):
    waypoints = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            if not line or ',' not in line:
                continue  # skip empty or bad lines
            try:
                lat, lon = map(float, line.split(','))
                waypoints.append((lat, lon))
            except ValueError:
                print(f"[WARNING] Skipping malformed line: {line}")
    return waypoints

def parse_nmea_gpgga(nmea_sentence):
    if not nmea_sentence.startswith("$GPGGA"):
        return None
    parts = nmea_sentence.split(",")
    if len(parts) < 6 or parts[2] == '' or parts[4] == '':
        return None
    
    def convert_to_decimal(coord, direction):
        if len(coord) < 4:  # Add safety check
            return None
        degrees = int(coord[:2])
        minutes = float(coord[2:])
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal
    
    try:
        lat = convert_to_decimal(parts[2], parts[3])
        lon = convert_to_decimal(parts[4], parts[5])
        if lat is None or lon is None:
            return None
        return lat, lon
    except (ValueError, IndexError):
        return None

def get_current_position(serial_conn, timeout=10):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            line = serial_conn.readline().decode(errors='ignore').strip()
            result = parse_nmea_gpgga(line)
            if result:
                return result
        except Exception as e:
            print(f"[WARNING] GPS reading error: {e}")
            continue
    print("[WARNING] GPS timeout - no valid position received")
    return None

def get_current_heading(prev_lat, prev_lon, curr_lat, curr_lon):
    return calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)

def main():
    port = "COM8"  # Change this depending on what port you use
    baud_rate = 9600  # This too
    
    # Initialize motor controller
    motor_controller = RoverMotorController()
    
    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"✅ Connected to GPS on {port} at {baud_rate} baud")
    except Exception as e:
        print(f"[ERROR] Could not open serial port: {e}")
        motor_controller.cleanup()
        return
    
    waypoints = load_gps_waypoints('gpslocations/sample-gpslocations.txt')
    if not waypoints:
        print("❌ No GPS waypoints loaded.")
        motor_controller.cleanup()
        return
    
    print("🚗 Starting Autonomous Navigation...\n")
    waypoint_index = 0
    prev_lat, prev_lon = None, None
    gps_fail_count = 0
    max_gps_fails = 5
    
    try:
        while waypoint_index < len(waypoints):
            try:
                position = get_current_position(ser, timeout=5)
                if position is None:
                    gps_fail_count += 1
                    print(f"[WARNING] GPS read failed ({gps_fail_count}/{max_gps_fails})")
                    if gps_fail_count >= max_gps_fails:
                        print("❌ Too many GPS failures. Stopping rover.")
                        break
                    motor_controller.stop()
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
                current_heading = get_current_heading(prev_lat, prev_lon, lat, lon)
                target_bearing = calculate_bearing(lat, lon, target_lat, target_lon)
                decision = decide_movement(current_heading, target_bearing)
                
                print(f"📍 Current: ({lat:.6f}, {lon:.6f})")
                print(f"🎯 Target:  ({target_lat:.6f}, {target_lon:.6f})")
                print(f"📏 Distance: {distance:.2f} m")
                print(f"🧭 Heading:  {current_heading:.2f}°")
                print(f"🧭 Bearing:  {target_bearing:.2f}°")
                print(f"🦾 Action:   {decision.upper()}")
                print("-" * 40)
                
                # Execute the movement decision
                execute_movement(decision, motor_controller)
                
                if distance < 3.0:  # Slightly relaxed threshold
                    print(f"✅ Reached waypoint {waypoint_index + 1}/{len(waypoints)}\n")
                    waypoint_index += 1
                    motor_controller.stop()
                    time.sleep(2)  # Pause between waypoints
                
                prev_lat, prev_lon = lat, lon
                time.sleep(0.5)  # Reduced sleep time for more responsive control
                
            except KeyboardInterrupt:
                print("\n🛑 Stopped by user.")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                motor_controller.stop()
                time.sleep(1)
                continue
                
    finally:
        motor_controller.cleanup()
        ser.close()
        print("🧹 Cleaned up resources.")

if __name__ == "__main__":  # Fixed the syntax error
    main()
