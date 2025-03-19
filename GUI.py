import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import capture_image, camera

class MeasurementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optical Scattering Measurement Device")
        self.root.geometry("500x550")

        self.picam2 = None  # Camera instance
        self.running = False
        self.measurement_type_var = tk.StringVar(value="both")  # Default: Measure both BRDF & BTDF

        ttk.Label(root, text="Measurement Type:").pack()
        ttk.Radiobutton(root, text="BRDF (Reflection Only)", variable=self.measurement_type_var, value="brdf").pack()
        ttk.Radiobutton(root, text="BTDF (Transmission Only)", variable=self.measurement_type_var, value="btdf").pack()
        ttk.Radiobutton(root, text="Both BRDF & BTDF", variable=self.measurement_type_var, value="both").pack()

        # Measurement Parameters
        ttk.Label(root, text="Measurement Parameters", font=("Arial", 12, "bold")).pack(pady=5)

        self.material_var = tk.StringVar()
        ttk.Label(root, text="Sample Material:").pack()
        self.material_entry = ttk.Entry(root, textvariable=self.material_var)
        self.material_entry.pack()

        self.angle_light_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Azimuthal Increment (°):").pack()
        self.angle_light_azimuthal_entry = ttk.Entry(root, textvariable=self.angle_light_azimuthal_var)
        self.angle_light_azimuthal_entry.pack()

        self.angle_light_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Radial Increment (°):").pack()
        self.angle_light_radial_entry = ttk.Entry(root, textvariable=self.angle_light_radial_var)
        self.angle_light_radial_entry.pack()

        self.angle_detector_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Azimuthal Increment (°):").pack()
        self.angle_detector_azimuthal_entry = ttk.Entry(root, textvariable=self.angle_detector_azimuthal_var)
        self.angle_detector_azimuthal_entry.pack()

        self.angle_detector_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Radial Increment (°):").pack()
        self.angle_detector_radial_entry = ttk.Entry(root, textvariable=self.angle_detector_radial_var)
        self.angle_detector_radial_entry.pack()

        self.num_steps_var = tk.IntVar()
        ttk.Label(root, text="Number of Steps:").pack()
        self.num_steps_entry = ttk.Entry(root, textvariable=self.num_steps_var)
        self.num_steps_entry.pack()

        self.exposure_var = tk.DoubleVar()
        ttk.Label(root, text="Exposure Time (μs):").pack()
        self.exposure_entry = ttk.Entry(root, textvariable=self.exposure_var)
        self.exposure_entry.pack()

        # Control Buttons
        ttk.Label(root, text="Automation Controls", font=("Arial", 12, "bold")).pack(pady=5)

        self.prepare_button = ttk.Button(root, text="Prepare Camera", command=self.prepare_camera)
        self.prepare_button.pack(pady=5)

        self.start_button = ttk.Button(root, text="Start Measurement", command=self.start_measurement, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Measurement", command=self.stop_measurement, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Export Button
        ttk.Button(root, text="Export Results", command=self.export_results).pack(pady=10)

        # Status Display
        self.status_label = ttk.Label(root, text="Status: Idle", foreground="blue")
        self.status_label.pack(pady=5)

    def prepare_camera(self):
        """Prepare the camera and apply configurations."""
        try:
            exposure = int(self.exposure_var.get())  # Ensure exposure is an integer
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid exposure time.")
            return

        self.picam2 = camera.initialize_camera(exposure)

        if self.picam2:
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Camera Ready", foreground="green")
            messagebox.showinfo("Camera Ready", "Camera is configured and ready for measurement.")
        else:
            messagebox.showerror("Error", "Camera initialization failed. Please check your setup.")

    def measurement_process(self):
        """Pass measurement parameters to capture_measurement()"""
        if not self.picam2:
            messagebox.showerror("Error", "Camera is not ready. Click 'Prepare Camera' first.")
            return

        measurement_type = self.measurement_type_var.get()

        self.status_label.config(text="Status: Running...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.running = True

        capture_image.capture_measurement(
            self.picam2,
            measurement_type,
            self.num_steps_var.get(),
            self.angle_light_azimuthal_var.get(),
            self.angle_light_radial_var.get(),
            self.angle_detector_azimuthal_var.get(),
            self.angle_detector_radial_var.get(),
        )

        self.status_label.config(text="Status: Completed")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def start_measurement(self):
        """Start the measurement process in a separate thread."""
        self.running = True
        threading.Thread(target=self.measurement_process, daemon=True).start()

    def stop_measurement(self):
        """Stop the measurement process."""
        self.running = False
        self.status_label.config(text="Status: Stopped")

    def export_results(self):
        """Export measurement results to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("Material, Steps, Light_Azimuthal, Light_Radial, Detector_Azimuthal, Detector_Radial\n")
                file.write(f"{self.material_var.get()}, {self.num_steps_var.get()}, {self.angle_light_azimuthal_var.get()}, {self.angle_light_radial_var.get()}, {self.angle_detector_azimuthal_var.get()}, {self.angle_detector_radial_var.get()}\n")
            messagebox.showinfo("Export", "Results exported successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementGUI(root)
    root.mainloop()