import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from distance_bearing import haversine, calculate_bearing


def decide_movement(current_heading, target_bearing, threshold=10):
    """
    Compares current heading with the bearing to the next waypoint.
    Returns a movement decision: 'forward', 'left', or 'right'.
    """
    # Normalize the angle difference to [-180, 180]
    error = (target_bearing - current_heading + 540) % 360 - 180

    if -threshold < error < threshold:
        return "forward"
    elif error <= -threshold:
        return "left"
    else:
        return "right"

def print_heading_info(current_lat, current_lon, next_lat, next_lon, current_heading):
    """
    Calculates distance and bearing to next waypoint and prints movement decision.
    """
    distance = haversine(current_lat, current_lon, next_lat, next_lon)
    bearing_to_target = calculate_bearing(current_lat, current_lon, next_lat, next_lon)
    decision = decide_movement(current_heading, bearing_to_target)

    print(f"Current Position:  ({current_lat:.6f}, {current_lon:.6f})")
    print(f"Next Waypoint:     ({next_lat:.6f}, {next_lon:.6f})")
    print(f"Distance to Target: {distance:.2f} m")
    print(f"Current Heading:    {current_heading:.2f}°")
    print(f"Bearing to Target:  {bearing_to_target:.2f}°")
    print(f"Decision:           {decision.upper()}")
    print("-" * 40)

    return decision

