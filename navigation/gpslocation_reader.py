import re
from geopy import Point

def dms_to_decimal(degrees_val, minutes_val, seconds_val, direction):
    """Convert DMS to decimal degrees."""
    decimal = float(degrees_val) + float(minutes_val) / 60 + float(seconds_val) / 3600
    if direction in ['S', 'W']:
        decimal *= -1
    return decimal

def parse_line_to_latlon(line):
    """
    Parses a single line of GPS input and returns (lat, lon) in decimal degrees.
    Accepts:
    - Decimal Degrees
    - DMS (e.g. 24°46'27"N 46°44'18"E)
    - DDM (e.g. 24°46.450'N, 46°44.316'E)
    - XYZ 3D format with lat/lon as part
    """
    line = line.strip()

    # Try: Decimal Degrees Format
    try:
        parts = [float(x) for x in re.findall(r'-?\d+\.\d+', line)]
        if len(parts) >= 2:
            return (parts[0], parts[1])
    except:
        pass

    # Try: DMS (Degrees Minutes Seconds)
    dms_regex = r'(\d+)[°:\s]+(\d+)\'?[\s:]*(\d+(?:\.\d+)?)"?\s*([NSEW])'
    dms_matches = re.findall(dms_regex, line)
    if len(dms_matches) >= 2:
        lat_dms = dms_matches[0]
        lon_dms = dms_matches[1]
        lat = dms_to_decimal(*lat_dms)
        lon = dms_to_decimal(*lon_dms)
        return (lat, lon)

    # Try: DDM (Degrees Decimal Minutes)
    ddm_regex = r'(\d+)[°:\s]+(\d+(?:\.\d+))\'?\s*([NSEW])'
    ddm_matches = re.findall(ddm_regex, line)
    if len(ddm_matches) >= 2:
        lat_deg, lat_min, lat_dir = ddm_matches[0]
        lon_deg, lon_min, lon_dir = ddm_matches[1]
        lat = dms_to_decimal(lat_deg, lat_min, 0, lat_dir)
        lon = dms_to_decimal(lon_deg, lon_min, 0, lon_dir)
        return (lat, lon)

    raise ValueError(f"Cannot parse GPS line: {line}")

# Read lines from a .txt file
with open("gpslocations/sample-gpslocations.txt", "r") as file:
    sample_inputs = file.readlines()



for line in sample_inputs:
    try:
        latlon = parse_line_to_latlon(line)
        print(f"[✓] Parsed: {line} → {latlon}")
    except Exception as e:
        print(f"[✗] Failed: {line} → {e}")
