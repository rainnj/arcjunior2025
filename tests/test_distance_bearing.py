import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from navigation.distance_bearing import haversine, calculate_bearing

def test_haversine():
    assert round(haversine(52.2296756, 21.0122287, 52.406374, 16.9251681)) == 278458

def test_bearing():
    bearing = calculate_bearing(52.2296756, 21.0122287, 52.406374, 16.9251681)
    assert 250 <= bearing <= 260  # Allow margin due to precision
