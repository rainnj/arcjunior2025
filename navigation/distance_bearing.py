from math import radians, cos, sin, asin, sqrt, atan2, degrees

def haversine(lat1, lon1, lat2, lon2):
  R= 6371000
  dlat = radians(lat2-lat1)
  dlon = radians(lon2-lon1)
  a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
  c = 2 * asin(sqrt(a))

  return R * c

def calculate_bearing(lat1, lon1, lat2, lon2):
  dlon = radians(lon2 - lon1)
  lat1 = radians(lat1)
  lat2 = radians(lat2)

x = sin(dlon) * cos(lat2)
y = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)

initial_bearing = atan2(x,y)
compass_bearing = (degrees(initial_bearing) + 360) % 360
return compass_bearing
