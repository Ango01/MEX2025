import tkinter as tk
from tkinter import ttk, messagebox
import threading
import capture_image, camera

class AutomationControlsWindow:
    def __init__(self, root, measurement_type, parameters):
        self.root = root
        self.root.title("Automation Controls")
        self.root.geometry("500x400")
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
        
        ttk.Button(root, text="Export Results", command=self.export_results).pack(pady=10)
        
        # Back button to return to measurement parameters
        self.back_button = ttk.Button(root, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)
    
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
        
        capture_image.capture_measurement(
            self.picam2,
            self.measurement_type,
            self.parameters["num_steps"],
            self.parameters["angle_light_azimuthal"],
            self.parameters["angle_light_radial"],
            self.parameters["angle_detector_azimuthal"],
            self.parameters["angle_detector_radial"],
        )
        
        self.status_label.config(text="Status: Completed", foreground="green")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def stop_measurement(self):
        self.running = False
        camera.stop_camera(self.picam2)
        self.status_label.config(text="Status: Stopped", foreground="red")
    
    def export_results(self):
        messagebox.showinfo("Export", "Results exported successfully!")
    
    def go_back(self):
        """Go back to the measurement parameters window."""
        from GUI.measurement_parameters import MeasurementParametersWindow
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementParametersWindow(new_root, self.measurement_type)
        new_root.mainloop()