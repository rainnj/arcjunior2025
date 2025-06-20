import time
import sys
sys.path.append('./navigation')  # ✅ Allows importing from /navigation

from distance_bearing import haversine, calculate_bearing
from headinglogic import decide_movement

def load_gps_waypoints(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()
    return [tuple(map(float, line.strip().split(','))) for line in lines]

def get_current_heading(prev_lat, prev_lon, curr_lat, curr_lon):
    return calculate_bearing(prev_lat, prev_lon, curr_lat, curr_lon)

def run_simulation(simulated_positions, target_waypoints):
    print("🚀 Starting Simulation Mode...\n")
    waypoint_index = 0

    for i in range(1, len(simulated_positions)):
        curr_lat, curr_lon = simulated_positions[i]
        prev_lat, prev_lon = simulated_positions[i - 1]

        if waypoint_index >= len(target_waypoints):
            print("✅ All waypoints reached!")
            break

        target_lat, target_lon = target_waypoints[waypoint_index]
        distance = haversine(curr_lat, curr_lon, target_lat, target_lon)
        current_heading = get_current_heading(prev_lat, prev_lon, curr_lat, curr_lon)
        target_bearing = calculate_bearing(curr_lat, curr_lon, target_lat, target_lon)
        decision = decide_movement(current_heading, target_bearing)

        print(f"[Simulated GPS] Position: ({curr_lat:.6f}, {curr_lon:.6f})")
        print(f"Target Waypoint:  ({target_lat:.6f}, {target_lon:.6f})")
        print(f"Distance to Target: {distance:.2f} m")
        print(f"Current Heading:    {current_heading:.2f}°")
        print(f"Target Bearing:     {target_bearing:.2f}°")
        print(f"Decision:           {decision.upper()}")
        print("-" * 50)

        if distance < 2.0:
            print(f"✅ Reached waypoint {waypoint_index + 1}/{len(target_waypoints)}")
            waypoint_index += 1

        time.sleep(1)

def run_live():
    import gpsd
    gpsd.connect()
    waypoints = load_gps_waypoints('gpslocations.sample-gpslocations.txt')  # ✅ fixed path

    if not waypoints:
        print("No GPS waypoints found.")
        return

    print("🛰️ Starting Live GPS Mode...\n")

    waypoint_index = 0
    prev_lat, prev_lon = None, None

    while waypoint_index < len(waypoints):
        try:
            packet = gpsd.get_current()
            lat = packet.lat
            lon = packet.lon
            time_utc = packet.time
            speed = packet.hspeed

            target_lat, target_lon = waypoints[waypoint_index]
            distance = haversine(lat, lon, target_lat, target_lon)

            if prev_lat is not None:
                current_heading = get_current_heading(prev_lat, prev_lon, lat, lon)
                target_bearing = calculate_bearing(lat, lon, target_lat, target_lon)
                decision = decide_movement(current_heading, target_bearing)

                print(f"Time: {time_utc}")
                print(f"Current Position: ({lat:.6f}, {lon:.6f})")
                print(f"Target Waypoint:  ({target_lat:.6f}, {target_lon:.6f})")
                print(f"Distance to Target: {distance:.2f} m")
                print(f"Current Heading:    {current_heading:.2f}°")
                print(f"Target Bearing:     {target_bearing:.2f}°")
                print(f"Decision:           {decision.upper()}")
                print("-" * 50)

                if distance < 2.0:
                    print(f"✅ Reached waypoint {waypoint_index + 1}/{len(waypoints)}")
                    waypoint_index += 1

            prev_lat, prev_lon = lat, lon
            time.sleep(1)

        except gpsd.NoFixError:
            print("No GPS fix yet...")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nNavigation stopped by user.")
            break

def main():
    print("🚀 Starting main()")
    if len(sys.argv) > 1 and sys.argv[1] == "--simulate":
        simulated_path = load_gps_waypoints('gpslocations/simulated-path.txt')  # ✅ fixed path
        waypoints = load_gps_waypoints('gpslocations/sample-gpslocations.txt')  # ✅ fixed path
        run_simulation(simulated_path, waypoints)
    else:
        run_live()

if __name__ == "__main__":
    main()
