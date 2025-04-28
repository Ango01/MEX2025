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
    step_counts = app.step_counts

    summary_text = (
        f"Measurement Type: {mtype}\n\n"
        f"Light Source - Total Azimuthal Steps: {step_counts['ls_az']} steps\n"
        f"Light Source - Total Radial Steps: {step_counts['ls_rad']} steps\n"
        f"Detector - Total Azimuthal Steps: {step_counts['det_az']} steps\n"
        f"Detector - Total Radial Steps: {step_counts['det_rad']} steps"
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
        spectral_content = "Monochrome"
        scatter_type = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        sample_rotations = [0.0]

        # Prepare angles
        incidence_angles = sorted(set(k[0] for k in app.bsdf_measurements.keys()))
        azimuth_angles = sorted(set(k[1] for k in app.bsdf_measurements.keys()))
        # Get radial angles safely
        first_key = next(iter(app.bsdf_measurements.keys()))
        radial_angles = sorted(set(r for (r, *_means) in app.bsdf_measurements[first_key]))

        # Group by (rotation, incidence)
        tis_data = {}
        bsdf_data = {}

        for inc_angle in incidence_angles:
            scatter_block = []  # Will be list of azimuth blocks (each is a list over radial)
            tis_value = 0.0

            for az_angle in azimuth_angles:
                key = (inc_angle, az_angle)
                if key not in app.bsdf_measurements:
                    print(f"Missing measurement for incidence={inc_angle}, azimuth={az_angle}, skipping...")
                    continue

                radial_measurements = sorted(app.bsdf_measurements[key])  # sorted by radial
                radial_intensities = [sum(means) / 3 for rad, *means in radial_measurements]

                scatter_block.append(radial_intensities)

                # TIS: sum of average intensity values
                tis_value += sum(radial_intensities)

            if not scatter_block:
                print(f"No data for incidence={inc_angle}, skipping...")
                continue

            # Save
            tis_data[(0.0, inc_angle)] = tis_value
            bsdf_data[(0.0, inc_angle)] = scatter_block  # list of lists (azimuth blocks)

        # Now generate the file
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