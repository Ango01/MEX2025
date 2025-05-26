import threading, os, logging
from tkinter import ttk, filedialog
from capture_image import run_full_measurement
from output_data import generate_zemax_bsdf_file, save_relative_errors

def create(app, container):
    """Create function for Step 5: Start the measurement process."""
    # Create main frame for this step
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)
    
    # Show summary of selected measurement parameters
    ttk.Label(frame, text="Measurement Parameters Summary: ").pack(anchor="w", pady=5)

    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"

    summary_text = (
        f"Measurement Type: {mtype}\n\n"
        f"Light Source - Azimuthal Step: {app.angle_step_sizes['ls_az']}° ({len(app.incidence_angles)} positions)\n"
        f"Light Source - Radial Step: {app.angle_step_sizes['ls_rad']}° ({len(app.light_radial_angles)} positions)\n"
        f"Detector - Azimuthal Step: {app.angle_step_sizes['det_az']}° ({len(app.det_azimuth_angles)} positions)\n"
        f"Detector - Radial Step: {app.angle_step_sizes['det_rad']}° ({len(app.det_radial_angles)} positions)\n\n"
    )

    logging.info(f"Measurement Type: {mtype}\n\n"
        f"Light Source - Azimuthal Step: {app.angle_step_sizes['ls_az']}° ({len(app.incidence_angles)} positions)\n"
        f"Light Source - Radial Step: {app.angle_step_sizes['ls_rad']}° ({len(app.light_radial_angles)} positions)\n"
        f"Detector - Azimuthal Step: {app.angle_step_sizes['det_az']}° ({len(app.det_azimuth_angles)} positions)\n"
        f"Detector - Radial Step: {app.angle_step_sizes['det_rad']}° ({len(app.det_radial_angles)} positions)\n"
    )

    # Layout for summary and navigation
    summary_row = ttk.Frame(frame)
    summary_row.pack(fill="x", padx=10, pady=5)

    # Show summary text
    summary_label = ttk.Label(summary_row, text=summary_text, justify="left")
    summary_label.grid(row=0, column=0, sticky="w")

    # Back button 
    ttk.Button(summary_row, text="Back", command=lambda: app.show_step(4)).grid(row=0, column=1, padx=10, sticky="e")

    # Buttons for measurement control
    button_frame = ttk.Frame(frame)
    button_frame.pack(pady=10)

    # Start button
    app.start_button = ttk.Button(button_frame, text="Start", command=lambda: start_measurement(app))
    app.start_button.pack(side="left", padx=5)

    # Stop button
    app.stop_button = ttk.Button(button_frame, text="Stop", command=lambda: stop_measurement(app))
    app.stop_button.pack(side="left", padx=5)

    # Save BSDF button (disabled until measurement completes)
    app.save_bsdf_button = ttk.Button(button_frame, text="Save BSDF", command=lambda: save_bsdf(app))
    app.save_bsdf_button.pack(side="left", padx=5)
    app.save_bsdf_button.config(state="disabled")  

def start_measurement(app):
    """Start measurement process."""
    # Validation checks
    if not hasattr(app, "camera") or app.camera is None:
        app.set_status("Camera not initialized.", "error")
        return

    if not hasattr(app, "dark_value"):
        app.set_status("Dark value missing. Capture or enter it first.", "error")
        return

    app.stop_requested = False
    app.start_button.config(state="disabled") # Disable start button

    def run_measurement_thread():
        """Background thread to run the measurement without blocking the GUI."""
        try:
            app.set_status("Starting full measurement...", "info")
            run_full_measurement(app)

            if not app.stop_requested:
                app.set_status("Measurement completed!", "success")
                app.save_bsdf_button.config(state="normal") # Enable BSDF save

        except Exception as e:
            logging.error(f"Measurement error: {e}")
            app.set_status(f"Measurement failed", "error")
        finally:
            app.start_button.config(state="normal") # Re-enable start button

    threading.Thread(target=run_measurement_thread, daemon=True).start()

def stop_measurement(app):
    """Request to stop the  process."""
    app.stop_requested = True
    app.set_status("Measurement stopped.", "warning")
    app.start_button.config(state="normal") # Allow restart
    app.bsdf_button.config(state="normal")

def save_bsdf(app):
    """Save BSDF data to a file in Zemax format."""
    # Open save dialog
    filename = filedialog.asksaveasfilename(
        defaultextension=".bsdf",
        filetypes=[("Zemax BSDF files", "*.bsdf"), ("All files", "*.*")],
        title="Save BSDF File"
    )

    if not filename:
        return

    try:
        # Set up required metadata
        symmetry = "Asymmetrical4D"
        spectral_content = "RGB"
        scatter_type = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        
        # Prepare angle lists
        sample_rotations = app.light_radial_angles         
        incidence_angles = app.incidence_angles           
        azimuth_angles = app.det_azimuth_angles            
        radial_angles = app.det_radial_angles              

        tis_data = {}    # Total integrated scatter values
        bsdf_data = {}   # Full 4D BSDF matrix

        # Build data from measurements
        for rot in sample_rotations: 
            for inc in incidence_angles:  
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

        # Write the .bsdf file 
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

        app.set_status("BSDF file and relative errors saved successfully!", "success")

        # Save relative errors alongside BSDF
        try:
            result_dir = os.path.dirname(filename)
            error_filename = os.path.splitext(os.path.basename(filename))[0] + "_relative_errors.csv"
            save_relative_errors(app, output_folder=result_dir, filename=error_filename)
        except Exception as e:
            logging.warning(f"Warning: Could not save relative errors: {e}")

    except Exception as e:
        logging.error(f"Error saving BSDF file: {e}")
        app.set_status(f"Error saving BSDF file", "error")
