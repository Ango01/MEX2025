from tkinter import ttk
from capture_image import run_full_measurement

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(frame, text="Click the button below to start the measurement process.").pack(anchor="w", pady=5)

    ttk.Button(frame, text="Start", command=lambda: start_measurement(app)).pack(pady=15)

def start_measurement(app):
    run_full_measurement(app)

        
