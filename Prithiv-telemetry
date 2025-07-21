import tkinter as tk
from tkinter import ttk
import time
import serial
import sys
import os
import csv

# Safe ranges for coloring and bar scales
TEMP_RANGE = (20, 40)
HUM_RANGE  = (30, 70)

# Open serial
try:
    ser = serial.Serial('COM8', 9600, timeout=0)  # non‑blocking
    time.sleep(2)
except Exception as e:
    print("Serial error:", e)
    sys.exit()

class RoverApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("FireFlies Rover Dashboard")
        self.configure(bg="#2E2E2E")
        self.geometry("440x880")

        # Load German flag image (must be in same folder)
        flag_path = r"D:\german_flag.png"
        orig = self.flag_img = tk.PhotoImage(file=flag_path)
        self.flag_img = orig.subsample(3, 3)

        # ttk theme & styles
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("Card.TFrame", background="#3C3F41", relief="flat")
        style.configure("Header.TLabel", background="#2E2E2E", foreground="white",
                        font=("Segoe UI", 16, "bold"))
        style.configure("Name.TLabel",   background="#3C3F41", foreground="#CCCCCC",
                        font=("Segoe UI", 10))
        style.configure("Value.TLabel",  background="#3C3F41", foreground="white",
                        font=("Segoe UI", 12, "bold"))
        style.configure("Status.TLabel", background="#2E2E2E", foreground="white",
                        font=("Segoe UI", 12, "italic"))
        style.configure("Cmd.TLabel",    background="#2E2E2E", foreground="#00C853",
                        font=("Segoe UI", 24, "bold"))
        style.configure("Bar.Horizontal.TProgressbar", troughcolor="#3C3F41",
                        background="#00BCD4", thickness=10)

        # Header with flag + title
        header = ttk.Frame(self, style="Card.TFrame", padding=(10,5))
        header.pack(pady=(20,10))
        ttk.Label(header, image=self.flag_img, background="#3C3F41").pack(side="left")
        ttk.Label(header, text=" Fireflies Rover Dashboard", style="Header.TLabel")\
            .pack(side="left", padx=10)

        # Telemetry container
        self.tel_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        self.tel_frame.pack(fill="both", padx=20, pady=10)

        # Define telemetry fields
        specs = [
            ("TEMP",   "Temperature (°C)",      TEMP_RANGE),
            ("HUM",    "Humidity (%)",          HUM_RANGE),
            ("GPS",    "GPS Status",            None),
            ("LIGHT",  "Light (lx)",            None),
            ("ORI",    "IMU Orientation",       None),
            ("BME",    "BME280 Status",         None),
            ("MQ2_RAW","MQ-2 Raw",              None),
            ("MQ2_V",  "MQ-2 Voltage (V)",      None),
        ]
        self.labels = {}
        self.bars   = {}

        for i, (key, name, rng) in enumerate(specs):
            card = ttk.Frame(self.tel_frame, style="Card.TFrame", padding=(10,8))
            card.grid(row=i, column=0, sticky="ew", pady=5)
            card.columnconfigure(1, weight=1)

            ttk.Label(card, text=name, style="Name.TLabel").grid(row=0, column=0, sticky="w")
            value_lbl = ttk.Label(card, text="--", style="Value.TLabel")
            value_lbl.grid(row=0, column=1, sticky="e")

            if rng:
                pb = ttk.Progressbar(card,
                                     style="Bar.Horizontal.TProgressbar",
                                     orient="horizontal",
                                     length=200,
                                     maximum=rng[1] - rng[0])
                pb.grid(row=1, column=0, columnspan=2, pady=(4,0), sticky="ew")
                self.bars[key] = (pb, rng)
            else:
                self.bars[key] = None

            self.labels[key] = (value_lbl, rng)

        # CSV telemetry log setup
        self.csv_path = "telemetry.csv"
        self.fieldnames = ["timestamp"] + [key for key, _, _ in specs]
        if not os.path.isfile(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()

        # Connection status
        self.status_lbl = ttk.Label(self, text="● Disconnected", style="Status.TLabel")
        self.status_lbl.pack(pady=(10,20))

        # Controls panel
        control_frame = ttk.Frame(self, style="Card.TFrame", padding=15)
        control_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(control_frame, text="Drive: W/A/S/D ● Brake: Space", style="Name.TLabel")\
            .grid(row=0, column=0, sticky="w")
        self.cmd_lbl = ttk.Label(control_frame, text="F", style="Cmd.TLabel")
        self.cmd_lbl.grid(row=1, column=0, pady=10)

        ttk.Label(control_frame, text="Servos: o/p  k/l  n/m", style="Name.TLabel")\
            .grid(row=2, column=0, sticky="w")
        self.servo1_lbl = ttk.Label(control_frame, text="S1: 90°", style="Value.TLabel")
        self.servo1_lbl.grid(row=3, column=0, sticky="w")
        self.servo2_lbl = ttk.Label(control_frame, text="S2: 90°", style="Value.TLabel")
        self.servo2_lbl.grid(row=4, column=0, sticky="w")
        self.servo3_lbl = ttk.Label(control_frame, text="S3: 90°", style="Value.TLabel")
        self.servo3_lbl.grid(row=5, column=0, sticky="w")

        # State
        self.last_tel    = time.time()
        self.current_cmd = 'F'
        self.pressed     = set()
        self.angle1 = 90
        self.angle2 = 90
        self.angle3 = 90

        # Key bindings
        for k in ("w","a","s","d","space","o","p","k","l","n","m"):
            self.bind(f"<KeyPress-{k}>",   self.on_press)
            self.bind(f"<KeyRelease-{k}>", self.on_release)
        self.focus_set()

        # Schedule loops (higher freq)
        self.after(10,   self.read_serial)   # telemetry every 10ms
        self.after(200,  self.check_conn)    # conn check every 200ms
        self.after(10,   self.send_cmd)      # send commands every 10ms

    def on_press(self, e):
        key = e.keysym.lower()
        if key in ("o","p","k","l","n","m"):
            self.handle_servo(key)
        else:
            self.pressed.add(key)
            self.update_drive_cmd()

    def on_release(self, e):
        key = e.keysym.lower()
        if key not in ("o","p","k","l","n","m"):
            self.pressed.discard(key)
            self.update_drive_cmd()

    def update_drive_cmd(self):
        if   "w"     in self.pressed: c = 'W'
        elif "s"     in self.pressed: c = 'S'
        elif "a"     in self.pressed: c = 'A'
        elif "d"     in self.pressed: c = 'D'
        elif "space" in self.pressed: c = 'F'
        else:                         c = 'F'
        self.current_cmd = c
        self.cmd_lbl["text"] = c

    def send_cmd(self):
        ser.write(f"{self.current_cmd}\n".encode())
        self.after(10, self.send_cmd)

    def handle_servo(self, key):
        if   key == 'o': self.angle1 = max(0, self.angle1 - 5)
        elif key == 'p': self.angle1 = min(270, self.angle1 + 5)
        elif key == 'k': self.angle2 = max(0, self.angle2 - 5)
        elif key == 'l': self.angle2 = min(180, self.angle2 + 5)
        elif key == 'n': self.angle3 = max(0, self.angle3 - 5)
        elif key == 'm': self.angle3 = min(180, self.angle3 + 5)

        self.servo1_lbl["text"] = f"S1: {self.angle1}°"
        self.servo2_lbl["text"] = f"S2: {self.angle2}°"
        self.servo3_lbl["text"] = f"S3: {self.angle3}°"
        ser.write(f"{key.upper()}\n".encode())

    def read_serial(self):
        raw = ser.read(ser.in_waiting or 1)
        for packet in raw.decode(errors='ignore').splitlines():
            line = packet.strip()
            if not line:
                continue

            # parse and log to CSV
            parts = dict(pair.split(":",1) for pair in line.split(",") if ":" in pair)
            row = {"timestamp": time.time()}
            for k in self.fieldnames:
                if k != "timestamp":
                    row[k] = parts.get(k, "")
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writerow(row)

            self.last_tel = time.time()
            for keyval in line.split(","):
                if ":" not in keyval:
                    continue
                k, v = keyval.split(":",1)
                lbl_tuple = self.labels.get(k)
                if not lbl_tuple:
                    continue
                lbl, rng = lbl_tuple
                lbl["text"] = v
                if rng:
                    try:
                        val = float(v)
                        lbl["background"] = "green" if rng[0] <= val <= rng[1] else "red"
                        pb, (mn,mx) = self.bars[k]
                        pb["value"] = max(0, min(val-mn, mx-mn))
                    except:
                        lbl["background"] = "yellow"
                else:
                    lbl["background"] = "#3C3F41"
            self.status_lbl["text"] = "● Connected"

        self.after(10, self.read_serial)

    def check_conn(self):
        if time.time() - self.last_tel > 3:
            self.status_lbl["text"] = "● Disconnected"
            for lbl, _ in self.labels.values():
                lbl["text"] = "--"
                lbl["background"] = "#3C3F41"
            for bar in filter(None, (self.bars[k] for k in self.bars)):
                bar[0]["value"] = 0
        self.after(200, self.check_conn)

    def on_close(self):
        ser.write(b"F\n")
        ser.close()
        self.destroy()

if __name__=="__main__":
    app = RoverApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
