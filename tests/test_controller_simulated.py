import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from controller import run_simulation, load_gps_waypoints

def test_controller_simulation():
    simulated_path = load_gps_waypoints("gpslocations/simulated-path.txt")
    waypoints = load_gps_waypoints("gpslocations/sample-gpslocations.txt")

    assert len(simulated_path) > 0
    assert len(waypoints) > 0

    run_simulation(simulated_path, waypoints)
