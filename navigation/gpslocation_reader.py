import gpsd
import time

# Connect to gpsd
gpsd.connect()

print("Reading live GPS data from u-blox 8... (Ctrl+C to stop)")

while True:
    try:
        packet = gpsd.get_current()
        lat = packet.lat
        lon = packet.lon
        time_utc = packet.time
        speed = packet.hspeed

        print(f"Time: {time_utc} | Lat: {lat:.6f} | Lon: {lon:.6f} | Speed: {speed:.2f} m/s")
        time.sleep(1)

    except gpsd.NoFixError:
        print("No GPS fix yet...")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopped.")
        break
