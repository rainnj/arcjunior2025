import time
import gpsd

from navigation.distance_bearing import haversine, calculate_bearing
from navigation.headinglogic import decide_movement

def load_gps_waypoints(filename):
    with open(filename, 'r') as file:
        return [tuple(map(float, line.strip().split(','))) for line in file]

def get_current_heading(prev_lat, prev_lon, curr_lat, curr_lon):
    return calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)

def main():
    try:
        gpsd.connect()
        print("✅ Connected to gpsd")
    except Exception as e:
        print(f"[ERROR] Failed to connect to gpsd: {e}")
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
            packet = gpsd.get_current()
            lat = packet.lat
            lon = packet.lon

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

        except gpsd.NoFixError:
            print("⚠️  No GPS fix yet... retrying.")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            break

if __name__ == "__main__":
    main()
