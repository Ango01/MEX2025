from tkinter import ttk
import threading
from capture_image import run_full_measurement

def create(app, container):
    """Create function for Step 5: Start the measurement process."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)
    
    # Measurement Summary Header
    ttk.Label(frame, text="Measurement Parameters: ").pack(anchor="w", pady=5)

    # Compose the summary text
    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
    step_sizes = {k: app.angle_inputs[k].get() for k in app.angle_inputs}
    step_counts = app.step_counts

    summary_text = (
        f"Measurement Type: {mtype}\n\n"
        f"Light Source - Azimuthal Step: {step_sizes['ls_az']}° ({step_counts['ls_az']} steps)\n"
        f"Light Source - Radial Step: {step_sizes['ls_rad']}° ({step_counts['ls_rad']} steps)\n"
        f"Detector - Azimuthal Step: {step_sizes['det_az']}° ({step_counts['det_az']} steps)\n"
        f"Detector - Radial Step: {step_sizes['det_rad']}° ({step_counts['det_rad']} steps)"
    )

    summary_label = ttk.Label(frame, text=summary_text, justify="left")
    summary_label.pack(anchor="w", padx=10)

    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=15)

    # Save buttons as app attributes
    app.start_button = ttk.Button(button_frame, text="Start", command=lambda: start_measurement(app))
    app.start_button.pack(side="left", padx=5)

    app.stop_button = ttk.Button(button_frame, text="Stop", command=lambda: stop_measurement(app))
    app.stop_button.pack(side="left", padx=5)

def start_measurement(app):
    """Function to start measurement process."""
    # Check if camera is initialized
    if not hasattr(app, "camera") or app.camera is None:
        app.set_status("Camera not initialized.", "error")
        return

    # Check if dark value has been set
    if not hasattr(app, "dark_value"):
        app.set_status("Dark value missing. Capture or enter it first.", "error")
        return

    app.stop_requested = False

    # Disable start button to prevent multiple clicks
    if hasattr(app, "start_button"):
        app.start_button.config(state="disabled")

    def run_measurement_thread():
        """Background thread to run the measurement without blocking the GUI."""
        try:
            app.set_status("Starting full measurement...", "info")
            run_full_measurement(app)
            if not app.stop_requested:
                app.set_status("Measurement completed!", "success")
        except Exception as e:
            print(f"Measurement error: {e}")
            app.set_status(f"Measurement failed: {e}", "error")
        finally:
            # Re-enable Start button in all cases
            if hasattr(app, "start_button"):
                app.start_button.config(state="normal")

    threading.Thread(target=run_measurement_thread, daemon=True).start()

def stop_measurement(app):
    """Function to request a stop of the measurement."""
    app.stop_requested = True
    app.set_status("Measurement stopped.", "warning")
    
    # Re-enable start button
    if hasattr(app, "start_button"):
        app.start_button.config(state="normal")
