from tkinter import ttk, filedialog
import threading
from capture_image import run_full_measurement
from process_image import generate_zemax_bsdf_file

def create(app, container):
    """Create function for Step 5: Start the measurement process."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)
    
    # Measurement Summary Header
    ttk.Label(frame, text="Measurement Parameters Summary: ").pack(anchor="w", pady=5)

    # Compose the summary text
    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"

    summary_text = (
        f"Measurement Type: {mtype}\n\n"
        f"Light Source - Azimuthal Step: {app.angle_step_sizes['ls_az']}° ({len(app.incidence_angles)} positions)\n"
        f"Light Source - Radial Step: {app.angle_step_sizes['ls_rad']}° ({len(app.light_radial_angles)} positions)\n"
        f"Detector - Azimuthal Step: {app.angle_step_sizes['det_az']}° ({len(app.det_azimuth_angles)} positions)\n"
        f"Detector - Radial Step: {app.angle_step_sizes['det_rad']}° ({len(app.det_radial_angles)} positions)\n\n"
    )

    summary_label = ttk.Label(frame, text=summary_text, justify="left")
    summary_label.pack(anchor="w", padx=10)

    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    # Save buttons as app attributes
    app.start_button = ttk.Button(button_frame, text="Start", command=lambda: start_measurement(app))
    app.start_button.pack(side="left", padx=5)

    app.stop_button = ttk.Button(button_frame, text="Stop", command=lambda: stop_measurement(app))
    app.stop_button.pack(side="left", padx=5)

    # Save BSDF button (initially disabled)
    app.save_bsdf_button = ttk.Button(button_frame, text="Save BSDF", command=lambda: save_bsdf(app))
    app.save_bsdf_button.pack(side="left", padx=5)
    app.save_bsdf_button.config(state="disabled")  # Disable initially

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

                # Enable Save BSDF button after successful measurement
                if hasattr(app, "save_bsdf_button"):
                    app.save_bsdf_button.config(state="normal")

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

def save_bsdf(app):
    """Save BSDF file after measurement."""
    filename = filedialog.asksaveasfilename(
        defaultextension=".bsdf",
        filetypes=[("Zemax BSDF files", "*.bsdf"), ("All files", "*.*")],
        title="Save BSDF File"
    )

    if not filename:
        return

    try:
        symmetry = "PlaneSymmetrical"
        spectral_content = "RGB"
        scatter_type = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        sample_rotations = [0]

        # Prepare angles
        sample_rotations = app.light_radial_angles         # Light source radial
        incidence_angles = app.incidence_angles            # Light source azimuth
        azimuth_angles = app.det_azimuth_angles            # Detector azimuth
        radial_angles = app.det_radial_angles              # Detector radial

        # Group by (rotation, incidence)
        tis_data = {}
        bsdf_data = {}

        for rot in sample_rotations:  # Light source radial
            for inc in incidence_angles:  # Light source azimuth
                scatter_grid = []
                tis_total = 0.0

                for az in azimuth_angles:
                    row = []
                    for rad in radial_angles:
                        key = (rot, inc, az, rad)
                        value = app.bsdf_measurements.get(key, (0.0, 0.0, 0.0))
                        row.append(value)
                        tis_total += sum(value)
                    scatter_grid.append(row)

                tis_data[(rot, inc)] = tis_total
                bsdf_data[(rot, inc)] = scatter_grid

        # Generate Zemax BSDF file in the required format
        generate_zemax_bsdf_file(
            filename=filename,
            symmetry=symmetry,
            spectral_content=spectral_content,
            scatter_type=scatter_type,
            sample_rotations=sample_rotations,
            incidence_angles=incidence_angles,
            azimuth_angles=azimuth_angles,
            radial_angles=radial_angles,
            tis_data=tis_data,
            bsdf_data=bsdf_data,
        )

        app.set_status("BSDF file saved successfully!", "success")
    except Exception as e:
        print(f"Error saving BSDF file: {e}")
        app.set_status(f"Error saving BSDF file: {e}", "error")
