import serial
import time
import csv
from datetime import datetime
from math import radians, cos, sin, asin, sqrt, atan2, degrees

# SETTINGS
COMPASS_PORT = "COM12"       # Make sure this matches your Arduino port
COMPASS_BAUD = 9600
LOG_FILE = "gps_navigation_log.csv"
ARRIVAL_THRESHOLD_METERS = 5
NAVIGATION_UPDATE_RATE = 1

DESTINATIONS = [
    (52.475548, 13.457868, "Destination one"),
]

# INIT
def init_serial():
    global serial_port
    serial_port = serial.Serial(COMPASS_PORT, COMPASS_BAUD, timeout=1)
    print(f"Connected to Arduino on {COMPASS_PORT}")

def read_from_serial():
    try:
        return serial_port.readline().decode('utf-8', errors='ignore').strip()
    except:
        return ""

# GPS Parser
def parse_gps_line(line):
    try:
        if line.startswith("$GPGGA"):
            parts = line.split(",")
            if len(parts) > 9:  # Ensure we have enough fields
                # Check if we have valid latitude data
                if parts[2] and parts[3] and parts[4] and parts[5]:
                    # Latitude format: DDMM.MMMMM
                    lat_str = parts[2]
                    lat_dir = parts[3]
                    # Longitude format: DDDMM.MMMMM
                    lon_str = parts[4]
                    lon_dir = parts[5]
                    
                    # Convert latitude
                    lat_deg = float(lat_str[:2]) if len(lat_str) > 2 else 0.0
                    lat_min = float(lat_str[2:]) if len(lat_str) > 2 else 0.0
                    lat = lat_deg + lat_min / 60.0
                    if lat_dir == 'S':
                        lat = -lat
                    
                    # Convert longitude
                    lon_deg = float(lon_str[:3]) if len(lon_str) > 3 else 0.0
                    lon_min = float(lon_str[3:]) if len(lon_str) > 3 else 0.0
                    lon = lon_deg + lon_min / 60.0
                    if lon_dir == 'W':
                        lon = -lon
                    
                    date_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    return lat, lon, date_str
    except Exception as e:
        print(f"GPS parsing error: {e}")
    return None, None, None

def convert_to_decimal(raw, direction):
    try:
        # Handle empty raw values
        if not raw:
            return 0.0
            
        # Convert DDDMM.MMMMM to decimal degrees
        deg = float(raw[:2]) if len(raw) > 2 else 0.0
        minutes = float(raw[2:]) if len(raw) > 2 else float(raw)
        decimal = deg + minutes / 60.0
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except ValueError:
        return 0.0

# Compass Parser
def parse_heading_line(line):
    try:
        if line.startswith("Heading:"):
            return float(line.split(":")[1].strip())
    except:
        pass
    return None

# Calculation Functions
def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in meters
    """
    # convert decimal degrees to radians 
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    
    # Radius of earth in meters (use 6371 for kilometers)
    r = 6371000
    return c * r

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the initial bearing (azimuth) from point 1 to point 2
    Returns bearing in degrees from north (0-360)
    """
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    dlon = lon2 - lon1
    x = sin(dlon) * cos(lat2)
    y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
    
    initial_bearing = atan2(x, y)
    
    # Convert bearing from radians to degrees (0-360)
    initial_bearing = degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    
    return compass_bearing

def calculate_relative_bearing(current_heading, target_bearing):
    """
    Calculate the relative bearing (difference between current heading and target bearing)
    Returns the angle you need to turn (positive = clockwise, negative = counter-clockwise)
    """
    relative_bearing = (target_bearing - current_heading) % 360
    if relative_bearing > 180:
        relative_bearing -= 360
    return relative_bearing

def bearing_to_cardinal(bearing):
    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                 "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]
    return cardinals[round(bearing / 22.5) % 16]

def get_turn_direction(relative_bearing):
    if relative_bearing > 0:
        return "right"
    elif relative_bearing < 0:
        return "left"
    else:
        return "straight"

def init_csv():
    with open(LOG_FILE, mode='w', newline='') as f:
        csv.writer(f).writerow([
            "LogTime", "Latitude", "Longitude", "Reported Date",
            "Destination", "DistanceToDest(m)", "TargetBearing", "Direction", 
            "CurrentHeading", "RelativeBearing", "TurnDirection", "TurnAngle"
        ])

def log_to_csv(lat, lon, date_str, destination_name, distance, bearing, direction, 
               real_heading, relative_bearing, turn_direction, turn_angle):
    with open(LOG_FILE, mode='a', newline='') as f:
        csv.writer(f).writerow([
            datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
            lat, lon, date_str, destination_name, distance, bearing, direction, 
            real_heading, relative_bearing, turn_direction, turn_angle
        ])

# MAIN LOOP
def main():
    print("Starting REAL GPS + COMPASS Navigation")
    init_serial()
    init_csv()
    latest_heading = None
    last_lat = last_lon = None

    while True:
        try:
            line = read_from_serial()
            if not line:
                continue

            if line.startswith("Heading:"):
                latest_heading = parse_heading_line(line)
                continue

            # Handle GPS data (with or without "GPS:" prefix)
            gps_line = line.replace("GPS:", "") if line.startswith("GPS:") else line
            lat, lon, date_str = parse_gps_line(gps_line)
            
            if lat is not None and lon is not None:
                last_lat, last_lon = lat, lon

                for dest_lat, dest_lon, dest_name in DESTINATIONS:
                    # Calculate distance and bearing
                    distance = haversine(lat, lon, dest_lat, dest_lon)
                    bearing = calculate_bearing(lat, lon, dest_lat, dest_lon)
                    direction = bearing_to_cardinal(bearing)
                    
                    # Prepare display
                    heading_display = f"{latest_heading:.1f}°" if latest_heading is not None else "None"
                    
                    # Calculate turn info if we have heading
                    hint = ""
                    relative_bearing = 0
                    turn_direction = ""
                    turn_angle = 0
                    
                    if latest_heading is not None:
                        relative_bearing = calculate_relative_bearing(latest_heading, bearing)
                        turn_direction = get_turn_direction(relative_bearing)
                        turn_angle = abs(relative_bearing)
                        hint = f"| Turn {turn_direction} {turn_angle:.1f}°"
                    
                    print(f"Position: ({lat:.6f}, {lon:.6f}) → {dest_name}")
                    print(f"Distance: {distance:.2f} m | Bearing: {bearing:.1f}° ({direction})")
                    print(f"Current heading: {heading_display} {hint}")
                    print("-" * 40)
                    
                    # Log data
                    log_to_csv(lat, lon, date_str, dest_name, distance, bearing, 
                             direction, latest_heading, relative_bearing,
                             turn_direction, turn_angle)

                    if distance < ARRIVAL_THRESHOLD_METERS:
                        print(f"Arrived at {dest_name}!")
                        return

            time.sleep(NAVIGATION_UPDATE_RATE)

        except KeyboardInterrupt:
            print("Stopped by user.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

    serial_port.close()
    print(f"Log saved: {LOG_FILE}")

if __name__ == "__main__":
    main()
