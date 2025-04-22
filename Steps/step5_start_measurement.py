from tkinter import ttk
from capture_image import capture_measurement

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(
        frame,
        text="Click the button below to start the measurement process."
    ).pack(anchor="w", pady=5)

    ttk.Button(
        frame,
        text="Start",
        command=lambda: start_measurement(app)
    ).pack(pady=15)

def start_measurement(app):
    try:
        measurement_type = app.measurement_type.get().lower()  # "brdf", "btdf", or "both"

        # Read angle increments from dropdowns
        ls_az = float(app.angle_inputs["ls_az"].get())
        ls_rad = float(app.angle_inputs["ls_rad"].get())
        det_az = float(app.angle_inputs["det_az"].get())
        det_rad = float(app.angle_inputs["det_rad"].get())

        # Fixed range can be hardcoded or added as a setting
        fixed_range = 20  # degrees (for example)

        app.set_status("Starting measurement...", "info")
        capture_measurement(
            picam2=app.camera,
            measurement_type=measurement_type,
            fixed_range=fixed_range,
            light_azimuthal_inc=ls_az,
            light_radial_inc=ls_rad,
            detector_azimuthal_inc=det_az,
            detector_radial_inc=det_rad
        )

        app.set_status("Measurement completed!", "success")

    except Exception as e:
        print(f"Measurement error: {e}")
        app.set_status(f"Error: {str(e)}", "error")
