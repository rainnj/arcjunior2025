import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from navigation.headinglogic import decide_movement

def test_heading_logic():
    assert decide_movement(0, 5) == "go_straight"
    assert decide_movement(0, 90) == "turn_right"
    assert decide_movement(0, 270) == "turn_left"
    assert decide_movement(350, 10) == "go_straight"
