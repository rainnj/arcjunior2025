import serial
import time
import csv
from datetime import datetime
from math import radians, cos, sin, asin, sqrt, atan2, degrees

# SETTINGS
COMPASS_PORT = "COM12"
COMPASS_BAUD = 115200
LOG_FILE = "gps_navigation_log.csv"
ARRIVAL_THRESHOLD_METERS = 5
NAVIGATION_UPDATE_RATE = 0.25  # 1 second

DESTINATIONS = [
    (52.475543, 13.458134, "one"),
]

# INIT
def init_serial():
    global serial_port
    serial_port = serial.Serial(COMPASS_PORT, COMPASS_BAUD, timeout=0.1)
    print(f"Connected to Arduino on {COMPASS_PORT}")

def read_from_serial():
    try:
        return serial_port.readline().decode('utf-8', errors='ignore').strip()
    except:
        return ""

# GPS Parser
def parse_gps_line(line):
    if line.startswith("GPS:$GPGGA"):
        parts = line.split(",")
        if len(parts) > 5 and parts[2] and parts[3] and parts[4] and parts[5]:
            lat = convert_to_decimal(parts[2], parts[3])
            lon = convert_to_decimal(parts[4], parts[5])
            if lat is not None and lon is not None:
                date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                return lat, lon, date_str
    elif line.startswith("GPS:$GPRMC"):
        parts = line.split(",")
        if len(parts) > 6 and parts[3] and parts[4] and parts[5] and parts[6]:
            lat = convert_to_decimal(parts[3], parts[4])
            lon = convert_to_decimal(parts[5], parts[6])
            if lat is not None and lon is not None:
                date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                return lat, lon, date_str
    return None, None, None

def convert_to_decimal(raw, direction):
    try:
        if not raw or not direction or len(raw) < 4:
            return None
        value = float(raw)
        deg = int(value / 100)
        min = value - deg * 100
        decimal = deg + min / 60
        if direction in ['S', 'W']:
            decimal = -decimal
        # Sanity check for valid ranges
        if direction in ['N', 'S'] and (decimal < -90 or decimal > 90):
            return None
        if direction in ['E', 'W'] and (decimal < -180 or decimal > 180):
            return None
        return decimal
    except:
        return None

# Compass Parser
def parse_heading_line(line):
    if line.startswith("Heading:"):
        try:
            return float(line.split(":")[1].strip())
        except:
            return None
    return None

# Calculations
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    return (degrees(atan2(x, y)) + 360) % 360

def bearing_to_cardinal(bearing):
    cardinals = ["N", "NE", "E", "SE", "S", "SW", "W", "NW", "N"]
    return cardinals[round(bearing / 45) % 8]

# ✅ WASD logic based on heading with ±20° margin
def get_direction_command(bearing, heading):
    if heading is None:
        return 'S'  # Stop if heading is unknown
    diff = (bearing - heading + 360) % 360
    if diff <= 20 or diff >= 340:
        return 'W'  # Forward
    elif diff > 20 and diff <= 180:
        return 'D'  # Turn right
    elif diff > 180 and diff < 340:
        return 'A'  # Turn left
    return 'S'

def init_csv():
    with open(LOG_FILE, mode='w', newline='') as f:
        csv.writer(f).writerow([
            "LogTime", "Latitude", "Longitude", "Reported Date",
            "Destination", "DistanceToDest", "Bearing", "Direction", "RealHeading"
        ])

def log_to_csv(lat, lon, date_str, destination_name, distance, bearing, direction, real_heading):
    with open(LOG_FILE, mode='a', newline='') as f:
        csv.writer(f).writerow([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            lat, lon, date_str, destination_name, distance, bearing, direction, real_heading
        ])

# MAIN LOOP
def main():
    print("Starting REAL GPS + COMPASS Navigation")
    init_serial()
    init_csv()
    latest_heading = None

    while True:
        try:
            line = read_from_serial()
            if not line:
                continue

            if line.startswith("Heading:"):
                latest_heading = parse_heading_line(line)

            elif line.startswith("GPS:$GPRMC") or line.startswith("GPS:$GPGGA"):
                lat, lon, date_str = parse_gps_line(line)
                if lat is not None and lon is not None:
                    for dest_lat, dest_lon, dest_name in DESTINATIONS:
                        distance = haversine(lat, lon, dest_lat, dest_lon)
                        bearing = calculate_bearing(lat, lon, dest_lat, dest_lon)
                        direction = bearing_to_cardinal(bearing)
                        heading_str = f"{latest_heading:.2f}" if latest_heading is not None else "None"
                        command = get_direction_command(bearing, latest_heading)
                        print(f"{command},")

                        print(f"({lat:.6f}, {lon:.6f}) -> {dest_name} | {distance:.2f} m | {direction} | Heading: {heading_str}")
                        log_to_csv(lat, lon, date_str, dest_name, distance, bearing, direction, latest_heading)

                        # ✅ Calculate direction command based on heading difference
                        
                        if distance < ARRIVAL_THRESHOLD_METERS:
                            print(f"Arrived at {dest_name}!")
                            return

                    time.sleep(NAVIGATION_UPDATE_RATE)

        except KeyboardInterrupt:
            print("Stopped by user.")
            break

    serial_port.close()
    print(f"Log saved: {LOG_FILE}")

if __name__ == "__main__":
    main()
