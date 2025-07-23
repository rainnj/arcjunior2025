# Add at top of file
import serial
import time
import csv
from datetime import datetime
from math import radians, cos, sin, asin, sqrt, atan2, degrees

COMPASS_PORT = "COM12"
COMPASS_BAUD = 9600
LOG_FILE = "gps_navigation_log.csv"
ARRIVAL_THRESHOLD_METERS = 5
NAVIGATION_UPDATE_RATE = 0.25  # seconds

DESTINATIONS = [
    (52.4764387, 13.4584166, "one"),
    (52.47639,   13.45834,   "two"),
    (52.47639,   13.45834,   "three"),
    (52.47645,   13.45817,   "four"),
    (52.47645,   13.45817,   "five"),
]

# --- New: utility functions ---
def haversine_distance(lat1, lon1, lat2, lon2):
    # returns distance in meters
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    # returns bearing in degrees [0..360)
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1)*sin(lat2) - sin(lat1)*cos(lat2)*cos(dlon)
    bearing = (degrees(atan2(x, y)) + 360) % 360
    return bearing

def direction_command(bearing, heading):
    if heading is None:
        return b'f'  # brake if no heading
    diff = (bearing - heading + 360) % 360
    if diff <= 20 or diff >= 340:
        return b'w'  # forward
    if diff > 180:
        return b'a'  # turn left
    return b'd'      # turn right

# --- Integration to send commands ---
def init_serial():
    global serial_port
    serial_port = serial.Serial(COMPASS_PORT, COMPASS_BAUD, timeout=0.1)
    time.sleep(2)  # ensure stable connection
    print(f"Connected to Arduino at {COMPASS_PORT}")

def send_command(cmd_byte):
    serial_port.write(cmd_byte)
    print(f"Sent command: {cmd_byte.decode()}")

# Update main loop
def main():
    init_serial()
    init_csv()
    latest_heading = None
    current_target = 0

    while current_target < len(DESTINATIONS):
        line = read_from_serial()
        if not line:
            continue

        if line.startswith("Heading:"):
            try:
                latest_heading = float(line.split(":")[1].strip())
            except:
                pass

        elif line.startswith("GPS:"):
            _, gpsdata = line.split("GPS:",1)
            lat_s, lon_s = gpsdata.split(",")[0].split("=")[1], gpsdata.split(",")[1].split("=")[1]
            try:
                lat = float(lat_s); lon = float(lon_s)
            except:
                continue

            dest_lat, dest_lon, dest_name = DESTINATIONS[current_target]
            distance = haversine_distance(lat, lon, dest_lat, dest_lon)
            bearing = calculate_bearing(lat, lon, dest_lat, dest_lon)
            cmd = direction_command(bearing, latest_heading)
            send_command(cmd)

            print(f"{cmd.decode()}, {lat:.6f},{lon:.6f} → {dest_name} | {distance:.2f} m | bear={bearing:.1f} ° | head={latest_heading}")
            log_to_csv(lat, lon, datetime.utcnow().isoformat(), dest_name, distance, bearing, cmd.decode(), latest_heading)

            if distance < ARRIVAL_THRESHOLD_METERS:
                print(f"✅ Arrived at {dest_name}")
                send_command(b'f')
                current_target += 1
            time.sleep(NAVIGATION_UPDATE_RATE)

    serial_port.close()
    print("Navigation complete.")

if __name__ == "__main__":
    main()
