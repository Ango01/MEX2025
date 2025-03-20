import tkinter as tk
from tkinter import ttk
from GUI.automation_controls import AutomationControlsWindow

class MeasurementParametersWindow:
    def __init__(self, root, measurement_type):
        self.root = root
        self.root.title("Measurement Parameters")
        self.root.geometry("500x450")
        self.measurement_type = measurement_type
        
        ttk.Label(root, text="Enter Measurement Parameters", font=("Arial", 14, "bold")).pack(pady=20)
        
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
        
        ttk.Button(root, text="Next", command=self.next_window).pack(pady=20)
        
        # Back button to return to measurement type selection
        self.back_button = ttk.Button(root, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)
    
    def next_window(self):
        # Destroy current window and open Automation Controls
        self.root.destroy()
        new_root = tk.Tk()
        AutomationControlsWindow(new_root, self.measurement_type, self.get_parameters())
        new_root.mainloop()
    
    def go_back(self):
        """Go back to the measurement type selection window."""
        from GUI.measurement_type import MeasurementTypeWindow
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementTypeWindow(new_root)
        new_root.mainloop()
    
    def get_parameters(self):
        return {
            "material": self.material_var.get(),
            "angle_light_azimuthal": self.angle_light_azimuthal_var.get(),
            "angle_light_radial": self.angle_light_radial_var.get(),
            "angle_detector_azimuthal": self.angle_detector_azimuthal_var.get(),
            "angle_detector_radial": self.angle_detector_radial_var.get(),
            "num_steps": self.num_steps_var.get(),
            "exposure": self.exposure_var.get(),
        }
