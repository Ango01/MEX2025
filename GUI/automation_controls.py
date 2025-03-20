import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import capture_image, camera, process_image
import pandas as pd

class AutomationControlsWindow:
    def __init__(self, root, measurement_type, parameters):
        self.root = root
        self.root.title("Automation Controls")
        self.root.geometry("500x450")
        self.measurement_type = measurement_type
        self.parameters = parameters
        self.picam2 = None
        self.running = False
        
        ttk.Label(root, text="Automation Controls", font=("Arial", 14, "bold")).pack(pady=20)

        self.status_label = ttk.Label(root, text="Status: Idle", foreground="blue")
        self.status_label.pack(pady=5)
        
        self.prepare_button = ttk.Button(root, text="Prepare Camera", command=self.prepare_camera)
        self.prepare_button.pack(pady=5)

        self.start_button = ttk.Button(root, text="Start Measurement", command=self.start_measurement, state=tk.DISABLED)
        self.start_button.pack(pady=5)

        self.stop_button = ttk.Button(root, text="Stop Measurement", command=self.stop_measurement, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.export_button = ttk.Button(root, text="Export Dataset", command=self.export_dataset)
        self.export_button.pack(pady=10)
        
        # If user selects "both", provide BSDF calculation option
        if self.measurement_type == "both":
            self.bsdf_button = ttk.Button(root, text="Get BSDF Dataset", command=self.compute_bsdf, state=tk.DISABLED)
            self.bsdf_button.pack(pady=10)
    
    def prepare_camera(self):
        try:
            exposure = int(self.parameters["exposure"])
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
    
    def start_measurement(self):
        self.running = True
        threading.Thread(target=self.measurement_process, daemon=True).start()
    
    def measurement_process(self):
        if not self.picam2:
            messagebox.showerror("Error", "Camera is not ready. Click 'Prepare Camera' first.")
            return

        self.status_label.config(text="Status: Running...", foreground="orange")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        dataset_file = f"scattering_data_{self.measurement_type}.csv"
        capture_image.capture_measurement(
            self.picam2,
            self.measurement_type,
            self.parameters["num_steps"],
            self.parameters["angle_light_azimuthal"],
            self.parameters["angle_light_radial"],
            self.parameters["angle_detector_azimuthal"],
            self.parameters["angle_detector_radial"],
            dataset_file
        )
        
        self.status_label.config(text=f"Status: {self.measurement_type.upper()} Dataset Ready", foreground="green")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        if self.measurement_type == "both":
            self.bsdf_button.config(state=tk.NORMAL)
    
    def stop_measurement(self):
        self.running = False
        camera.stop_camera(self.picam2)
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def export_dataset(self):
        dataset_file = f"scattering_data_{self.measurement_type}.csv"
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            df = pd.read_csv(dataset_file)
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Export", f"{self.measurement_type.upper()} Dataset exported successfully!")
    
    def compute_bsdf(self):
        process_image.compute_bsdf("scattering_data_brdf.csv", "scattering_data_btdf.csv", "scattering_data_bsdf.csv")
        messagebox.showinfo("BSDF Computation", "BSDF dataset has been generated successfully!")