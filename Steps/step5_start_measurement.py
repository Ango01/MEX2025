from tkinter import ttk
from capture_image import run_full_measurement

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(frame, text="Click the button below to start the measurement process.").pack(anchor="w", pady=5)

    ttk.Button(frame, text="Start", command=lambda: start_measurement(app)).pack(pady=15)

def start_measurement(app):
    try:
        # Get angle values from comboboxes BEFORE doing any hardware work
        app.ls_az_step = float(app.angle_inputs["ls_az"].get())
        app.ls_rad_step = float(app.angle_inputs["ls_rad"].get())
        app.det_az_step = float(app.angle_inputs["det_az"].get())
        app.det_rad_step = float(app.angle_inputs["det_rad"].get())

        # Then run the full measurement (which accesses app.ls_az_step, etc.)
        run_full_measurement(app)

    except Exception as e:
        app.set_status(f"Error: {str(e)}", "error")

        
