import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import time
import capture_image, camera

class MeasurementGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Optical Scattering Measurement Device")
        self.root.geometry("500x400")
        
        # Measurement Parameters
        ttk.Label(root, text="Measurement Parameters", font=("Arial", 12, "bold")).pack(pady=5)

        self.material_var = tk.StringVar()
        ttk.Label(root, text="Sample Material:").pack()
        self.material_entry = ttk.Entry(root, textvariable=self.material_var)
        self.material_entry.pack()
        
        self.angle_var = tk.DoubleVar()
        ttk.Label(root, text="Angle Increment (°):").pack()
        self.angle_entry = ttk.Entry(root, textvariable=self.angle_var)
        self.angle_entry.pack()
        
        self.exposure_var = tk.DoubleVar()
        ttk.Label(root, text="Exposure Time:").pack()
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
        
        self.running = False

    def prepare_camera(self):
        exposure = self.exposure_var.get()
    
        if not exposure:
            messagebox.showerror("Error", "Please enter an exposure time.")
            return
        
        self.picam2 = camera.initialize_camera(exposure)
        self.start_button.config(state=tk.NORMAL)
        self.status_label.config(text="Status: Camera Ready", foreground="green")

    def measurement_process(self):
        self.status_label.config(text="Status: Running...")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        angle_increment = int(self.angle_var.get())

        num_steps = 10 # Capture 10 images at different angles

        for i in range(num_steps):  # Simulate 10 steps of measurement
            if not self.running:
                break
            
            current_angle = i * angle_increment
            print(f"Moving to {current_angle} degrees")
            
            image_file = capture_image.capture_image(self.picam2, current_angle)
            print(f"Image saved at: {image_file}")

            time.sleep(1)  # Simulating measurement time
        
        self.status_label.config(text="Status: Completed")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def start_measurement(self):
        self.running = True
        threading.Thread(target=self.measurement_process, daemon=True).start()
    
    def stop_measurement(self):
        self.running = False
        self.status_label.config(text="Status: Stopped")
    
    def export_results(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All Files", "*.*")])
        if file_path:
            with open(file_path, "w") as file:
                file.write("Material, Angle, Exposure\n")
                file.write(f"{self.material_var.get()}, {self.angle_var.get()}, {self.exposure_var.get()}\n")
            messagebox.showinfo("Export", "Results exported successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MeasurementGUI(root)
    root.mainloop()
