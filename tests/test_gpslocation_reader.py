from navigation.gpslocation_reader import read_sample_gps

def test_gpslocation_reader():
    waypoints = read_sample_gps("gpslocations/sample-gpslocations.txt")
    assert isinstance(waypoints, list)
    assert all(isinstance(wp, tuple) and len(wp) == 2 for wp in waypoints)
