import tkinter as tk
from tkinter import ttk, messagebox

class MeasurementParametersWindow:
    """Class to create a window for entering measurement parameters."""
    def __init__(self, root, measurement_type):
        self.root = root
        self.root.title("Measurement Parameters")
        self.root.geometry("500x550")
        self.measurement_type = measurement_type

        ttk.Label(root, text="Enter Measurement Parameters", font=("Arial", 14, "bold")).pack(pady=20)

        # Sample Material
        self.material_var = tk.StringVar()
        ttk.Label(root, text="Sample Material:").pack(pady=10)
        self.material_entry = ttk.Entry(root, textvariable=self.material_var).pack()

        # Dropdown options
        angle_options = [1.0, 2.5, 5.0, 10.0, 15.0, 30.0]
        step_options = [1, 3, 5, 10, 15, 20]

        # Light Source Azimuthal Increment
        self.angle_light_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Azimuthal Increment (°):").pack(pady=10)
        self.angle_light_azimuthal_entry = ttk.Combobox(root, textvariable=self.angle_light_azimuthal_var, values=angle_options, state="readonly").pack()

        # Light Source Radial Increment
        self.angle_light_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Radial Increment (°):").pack(pady=10)
        self.angle_light_radial_entry = ttk.Combobox(root, textvariable=self.angle_light_radial_var, values=angle_options, state="readonly").pack()

        # Detector Azimuthal Increment
        self.angle_detector_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Azimuthal Increment (°):").pack(pady=10)
        self.angle_detector_azimuthal_entry = ttk.Combobox(root, textvariable=self.angle_detector_azimuthal_var, values=angle_options, state="readonly").pack()

        # Detector Radial Increment
        self.angle_detector_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Radial Increment (°):").pack(pady=10)
        self.angle_detector_radial_entry = ttk.Combobox(root, textvariable=self.angle_detector_radial_var, values=angle_options, state="readonly").pack()

        # Number of Steps for light source
        self.light_num_steps_var = tk.IntVar()
        ttk.Label(root, text="Number of Steps (light source):").pack(pady=10)
        self.num_steps_entry = ttk.Combobox(root, textvariable=self.light_num_steps, values=step_options, state="readonly").pack()

        # Number of Steps for detector
        self.detector_num_steps_var = tk.IntVar()
        ttk.Label(root, text="Number of Steps (detector):").pack(pady=10)
        self.num_steps_entry = ttk.Combobox(root, textvariable=self.detetcor_num_steps_var, values=step_options, state="readonly").pack()
        
        ttk.Button(root, text="Next", command=self.next_window).pack(pady=20)

        # Back button
        self.back_button = ttk.Button(root, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)

        self.update_angle_inputs()
    
    def update_angle_inputs(self): ###--- UPDATE: range for BRDF/BTDF
        """Enable or disable angle fields based on measurement type selection."""
        if self.measurement_type == "brdf":
            self.angle_detector_radial_entry.config(state=tk.DISABLED)
            self.angle_detector_radial_var.set(0.0)  # Reset unused field to zero

        elif self.measurement_type == "btdf":
            self.angle_light_radial_entry.config(state=tk.DISABLED)
            self.angle_light_radial_var.set(0.0)  # Reset unused field to zero
    
    def next_window(self):
        """Close the current window and open the Automation Controls window."""
        if (
            self.material_var.get().strip() == "" or
            self.angle_light_azimuthal_var.get() == 0.0 or
            self.angle_detector_radial_var.get() == 0.0 or
            self.angle_detector_azimuthal_var.get() == 0.0 or
            self.angle_detector_radial_var.get() == 0.0 or
            self.light_num_steps.get() == 0 or
            self.detector_num_steps.get()  == 0
        ):
            messagebox.showwarning("Missing Input", "Please fill in all measurement parameters before continuing.")
            return
        
        from GUI.automation_controls import AutomationControlsWindow  # Delayed import
        self.root.destroy()
        new_root = tk.Tk()
        AutomationControlsWindow(new_root, self.measurement_type, self.get_parameters())
        new_root.mainloop()
    
    def go_back(self):
        """Go back to the Measurement Type window."""
        from GUI.measurement_type import MeasurementTypeWindow  # Delayed import
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementTypeWindow(new_root)
        new_root.mainloop()
    
    def get_parameters(self):
        """Collect and return the measurement parameters entered by the user."""
        return {
            "material": self.material_var.get(),
            "angle_light_azimuthal": self.angle_light_azimuthal_var.get(),
            "angle_light_radial": self.angle_light_radial_var.get(),
            "angle_detector_azimuthal": self.angle_detector_azimuthal_var.get(),
            "angle_detector_radial": self.angle_detector_radial_var.get(),
            "num_steps_light": self.light_num_steps.get(),
            "num_steps_detector": self.detector_num_steps.get()
        }
