import tkinter as tk
import random
import time

# ----------------------------
# Safe Ranges
TEMP_RANGE = (20, 40)
HUM_RANGE = (30, 70)
# ----------------------------

# Global variable to track last update time
last_update_time = time.time()

def get_random_sensor_data():
    return {
        "TEMP": round(random.uniform(15, 50), 1),
        "HUM": round(random.uniform(20, 90), 1),
        "ARUCO_ID": random.randint(1, 10),
        "STATUS": "connected"
    }

def update_data():
    global last_update_time

    # Simulate sensor data
    data = get_random_sensor_data()
    temp = data["TEMP"]
    hum = data["HUM"]
    aruco = data["ARUCO_ID"]
    
    # Update time
    last_update_time = time.time()

    # Update temperature
    temp_label["text"] = f"{temp} °C"
    temp_label["bg"] = "green" if TEMP_RANGE[0] <= temp <= TEMP_RANGE[1] else "red"

    # Update humidity
    hum_label["text"] = f"{hum} %"
    hum_label["bg"] = "green" if HUM_RANGE[0] <= hum <= HUM_RANGE[1] else "red"

    # Update Aruco ID
    aruco_label["text"] = f"{aruco}"
    aruco_label["bg"] = "lightblue"

    # Update connection status
    status_label["text"] = "Connected"
    status_label["fg"] = "green"

    # Call this function again after 1000ms
    root.after(1000, check_connection)

def check_connection():
    global last_update_time

    # If last update was more than 3 seconds ago, assume disconnected
    if time.time() - last_update_time > 3:
        status_label["text"] = "Disconnected"
        status_label["fg"] = "red"
    else:
        update_data()

# ----------------------------
# Tkinter GUI Setup
# ----------------------------
root = tk.Tk()
root.title("Rover Telemetry Monitor")
root.geometry("300x250")
root.configure(bg="#f0f0f0")

# Labels
tk.Label(root, text="Temperature:", font=("Arial", 12)).pack(pady=5)
temp_label = tk.Label(root, text="-- °C", font=("Arial", 14), width=15)
temp_label.pack()

tk.Label(root, text="Humidity:", font=("Arial", 12)).pack(pady=5)
hum_label = tk.Label(root, text="-- %", font=("Arial", 14), width=15)
hum_label.pack()

tk.Label(root, text="Aruco ID:", font=("Arial", 12)).pack(pady=5)
aruco_label = tk.Label(root, text="--", font=("Arial", 14), width=15)
aruco_label.pack()

tk.Label(root, text="Status:", font=("Arial", 12)).pack(pady=5)
status_label = tk.Label(root, text="Disconnected", font=("Arial", 14))
status_label.pack()

# Start updating
update_data()

# Run the GUI
root.mainloop()
