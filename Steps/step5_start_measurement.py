from tkinter import ttk
from capture_image import run_full_measurement

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(frame, text="Click the button below to start the measurement process.").pack(anchor="w", pady=5)

    # Start and Stop button row
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=15)

    ttk.Button(button_frame, text="Start", command=lambda: start_measurement(app)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Stop", command=lambda: stop_measurement(app)).pack(side="left", padx=5)

def start_measurement(app):
    if not hasattr(app, "camera") or app.camera is None:
        app.set_status("Camera not initialized.", "error")
        return

    if not hasattr(app, "dark_value"):
        app.set_status("Dark value missing. Capture or enter it first.", "error")
        return
    
    app.stop_requested = False

    app.set_status("Starting full measurement...", "info")

    # Disable Start button
    if hasattr(app, "start_button"):
        app.start_button.config(state="disabled")

    try:
        run_full_measurement(app)
    except Exception as e:
        print(f"Measurement error: {e}")
        app.set_status(f"Measurement failed: {e}", "error")
        # Re-enable Start button on failure
        if hasattr(app, "start_button"):
            app.start_button.config(state="normal")

def stop_measurement(app):
    app.stop_requested = True
    app.set_status("Stop requested. Waiting for current step to finish...", "warning")

    # Re-enable Start button after stop
    if hasattr(app, "start_button"):
        app.start_button.config(state="normal")

        
