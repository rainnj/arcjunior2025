def normalize_angle(angle):
    """Normalize angle to 0-360 degrees"""
    return angle % 360

def angle_difference(angle1, angle2):
    """Calculate the shortest angular difference between two angles"""
    diff = angle2 - angle1
    # Normalize to -180 to 180
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360
    return diff

def decide_movement(current_heading, target_bearing, tolerance=10):
    """
    Decide rover movement based on current heading and target bearing
    
    Args:
        current_heading: Current direction rover is facing (0-360 degrees)
        target_bearing: Direction rover should go (0-360 degrees)  
        tolerance: Acceptable angle difference to go straight (degrees)
    
    Returns:
        String: Movement decision ('forward', 'left', 'right', 'sharp_left', 'sharp_right')
    """
    
    # Normalize angles
    current_heading = normalize_angle(current_heading)
    target_bearing = normalize_angle(target_bearing)
    
    # Calculate angle difference
    angle_diff = angle_difference(current_heading, target_bearing)
    
    # Decision logic
    if abs(angle_diff) <= tolerance:
        return "forward"
    elif angle_diff > 0:
        # Need to turn right
        if angle_diff > 45:
            return "sharp_right"
        else:
            return "right"
    else:
        # Need to turn left
        if angle_diff < -45:
            return "sharp_left"
        else:
            return "left"

def calculate_turn_duration(angle_difference, base_turn_time=0.5):
    """
    Calculate how long to turn based on angle difference
    
    Args:
        angle_difference: Angle to turn (degrees)
        base_turn_time: Base time for a standard turn (seconds)
    
    Returns:
        float: Turn duration in seconds
    """
    # Scale turn time based on angle
    abs_angle = abs(angle_difference)
    
    if abs_angle <= 10:
        return 0.1  # Very small adjustment
    elif abs_angle <= 30:
        return base_turn_time * 0.5  # Small turn
    elif abs_angle <= 90:
        return base_turn_time  # Standard turn
    else:
        return base_turn_time * 1.5  # Large turn

# Test function
def test_heading_logic():
    """Test the heading logic with various scenarios"""
    test_cases = [
        (0, 0, "forward"),      # Straight ahead
        (0, 45, "right"),       # Turn right
        (0, 315, "left"),       # Turn left (through 0)
        (90, 180, "right"),     # Turn right 90 degrees
        (180, 90, "left"),      # Turn left 90 degrees
        (0, 180, "sharp_right"), # Turn around (either direction works)
        (45, 5, "left"),        # Small left turn
        (315, 45, "right"),     # Turn right through 0
    ]
    
    print("Testing heading logic:")
    print("-" * 50)
    
    for current, target, expected in test_cases:
        result = decide_movement(current, target)
        status = "✅" if result == expected else "❌"
        angle_diff = angle_difference(current, target)
        
        print(f"{status} Current: {current:3d}° → Target: {target:3d}° | "
              f"Diff: {angle_diff:+4.0f}° | Decision: {result:11s} | Expected: {expected}")

if __name__ == "__main__":
    test_heading_logic()
