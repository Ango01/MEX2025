import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import capture_image, camera, process_image
import threading

class AutomationControlsWindow:
    """Class to handle the automation controls for the measurement process."""
    def __init__(self, root, measurement_type, parameters):
        self.root = root
        self.root.title("Automation Controls")
        self.root.geometry("500x450")
        self.measurement_type = measurement_type
        self.parameters = parameters
        self.picam2 = None
        
        ttk.Label(root, text="Automation Controls", font=("Arial", 14, "bold")).pack(pady=20)

        self.status_label = ttk.Label(root, text="Status: Idle", foreground="blue")
        self.status_label.pack(pady=5)
        
        self.prepare_button = ttk.Button(root, text="Prepare Camera", command=self.prepare_camera)
        self.prepare_button.pack(pady=5)

        self.start_button = ttk.Button(root, text="Start Measurement", command=self.start_measurement, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Measurement", command=self.stop_measurement, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.export_button = ttk.Button(root, text="Export Dataset", command=self.export_dataset, state=tk.DISABLED)
        self.export_button.pack(pady=10)
        
        # If user selects "both", provide BSDF calculation option
        if self.measurement_type == "both":
            self.bsdf_button = ttk.Button(root, text="Get BSDF Dataset", command=self.compute_bsdf, state=tk.DISABLED)
            self.bsdf_button.pack(pady=10)

        self.back_button = ttk.Button(root, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)
    
    def prepare_camera(self):
        """Initialize and configure the camera for measurement."""
        try:
            exposure = self.parameters["exposure"]
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid exposure time.")
            return
        
        print(f"Exposure time: ", exposure)
        self.picam2 = camera.initialize_camera(exposure)

        if self.picam2:
            self.start_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Camera Ready", foreground="green")
        else:
            messagebox.showerror("Error", "Camera initialization failed. Please check your setup.")
    
    def start_measurement(self):
        """Perform the measurement process and capture scattering data in a separate thread."""
        self.status_label.config(text="Status: Running...", foreground="blue")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)  

        # Run the measurement process in a separate thread to avoid freezing the GUI
        measurement_thread = threading.Thread(target=self.run_measurement_process, daemon=True)
        measurement_thread.start()

    def run_measurement_process(self):
        """Captures measurement images and saves scattering data."""
        capture_image.capture_measurement(
            self.picam2,
            self.measurement_type,
            self.parameters["num_steps"],
            self.parameters["angle_light_azimuthal"],
            self.parameters["angle_light_radial"],
            self.parameters["angle_detector_azimuthal"],
            self.parameters["angle_detector_radial"]
        )
        
        self.status_label.config(text=f"Status: {self.measurement_type.upper()} Dataset Ready", foreground="green")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.NORMAL)
        
        if self.measurement_type == "both":
            self.bsdf_button.config(state=tk.NORMAL)
    
    def stop_measurement(self):
        """Stop the measurement process."""
        camera.stop_camera(self.picam2)
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def export_dataset(self):
        """Export the captured measurement dataset as a CSV file."""
        dataset_file = f"scattering_data_{self.measurement_type}.csv"

        # Open a file save dialog to select export location
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            df = pd.read_csv(dataset_file)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Export", f"{self.measurement_type.upper()} Dataset exported successfully!")
    
    def compute_bsdf(self):
        """Compute the BSDF dataset by combining BRDF and BTDF data."""
        process_image.compute_bsdf("scattering_data_brdf.csv", "scattering_data_btdf.csv", "scattering_data_bsdf.csv")
        messagebox.showinfo("BSDF Computation", "BSDF dataset has been generated successfully!")
    
    def go_back(self):
        """Go back to the measurement parameters window."""
        from GUI.measurement_parameters import MeasurementParametersWindow  # Delayed import
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementParametersWindow(new_root, self.measurement_type_var.get())
        new_root.mainloop()