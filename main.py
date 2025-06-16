import serial
import time

from navigation.distance_bearing import haversine, calculate_bearing
from navigation.headinglogic import decide_movement

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
        degrees = int(coord[:2])
        minutes = float(coord[2:])
        decimal = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal *= -1
        return decimal

    lat = convert_to_decimal(parts[2], parts[3])
    lon = convert_to_decimal(parts[4], parts[5])
    return lat, lon

def get_current_position(serial_conn):
    while True:
        line = serial_conn.readline().decode(errors='ignore').strip()
        result = parse_nmea_gpgga(line)
        if result:
            return result

def get_current_heading(prev_lat, prev_lon, curr_lat, curr_lon):
    return calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)

def main():
    port = "COM8"  #we have to change this depending on what port we use
    baud_rate = 3600 #this too

    try:
        ser = serial.Serial(port, baud_rate, timeout=1)
        print(f"✅ Connected to GPS on {port} at {baud_rate} baud")
    except Exception as e:
        print(f"[ERROR] Could not open serial port: {e}")
        return

    waypoints = load_gps_waypoints('gpslocations/sample-gpslocations.txt')

    if not waypoints:
        print("❌ No GPS waypoints loaded.")
        return

    print("🚗 Starting Autonomous Navigation...\n")

    waypoint_index = 0
    prev_lat, prev_lon = None, None

    while waypoint_index < len(waypoints):
        try:
            lat, lon = get_current_position(ser)

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

            if distance < 2.0:
                print(f"✅ Reached waypoint {waypoint_index + 1}/{len(waypoints)}\n")
                waypoint_index += 1

            prev_lat, prev_lon = lat, lon
            time.sleep(1)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

if __name__ == "__main__":
    main()
