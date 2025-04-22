from tkinter import ttk
from capture_image import run_full_measurement

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(frame, text="Click the button below to start the measurement process.").pack(anchor="w", pady=5)

    ttk.Button(frame, text="Start", command=lambda: start_measurement(app)).pack(pady=15)

def start_measurement(app):
    if not hasattr(app, "camera") or app.camera is None:
        app.set_status("Camera not initialized.", "error")
        return

    if not hasattr(app, "dark_value"):
        app.set_status("Dark value missing. Capture or enter it first.", "error")
        return

    app.set_status("Starting full measurement...", "info")

    try:
        run_full_measurement(app)
    except Exception as e:
        print(f"Measurement error: {e}")
        app.set_status(f"Measurement failed: {e}", "error")

        
