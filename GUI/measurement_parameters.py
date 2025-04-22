import tkinter as tk
from tkinter import ttk, messagebox
from GUI.automation_controls import AutomationControlsWindow
from GUI.measurement_type import MeasurementTypeWindow

class MeasurementParametersWindow:
    """Class to create a window for entering measurement parameters."""
    def __init__(self, root, measurement_type):
        self.root = root
        self.root.title("Measurement Parameters")
        self.root.geometry("500x700")
        self.measurement_type = measurement_type

        ttk.Label(root, text="Enter Measurement Parameters", font=("Arial", 14, "bold")).pack(pady=20)

        # Sample Material
        self.material_var = tk.StringVar()
        ttk.Label(root, text="Sample Material:").pack(pady=10)
        self.material_entry = ttk.Entry(root, textvariable=self.material_var)
        self.material_entry.pack()

        # Define fixed range depending on measurement type (detector from 8 to 90/170? and light source from 20)
        if self.measurement_type == "brdf":
            self.fixed_range = 180
            self.range_label_text = "Fixed Range: 0° to 180°"
        elif self.measurement_type == "btdf":
            self.fixed_range = 180
            self.range_label_text = "Fixed Range: 180° to 360°"
        else:  # both
            self.fixed_range = 360
            self.range_label_text = "Fixed Range: 0° to 360°"

        # Dropdown options
        angle_options = [1.0, 2.5, 5.0, 10.0, 15.0, 30.0]

        # ---- Light Source Azimuthal ----
        self.angle_light_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Azimuthal Increment (°):").pack(pady=5)
        ttk.Label(root, text=self.range_label_text, foreground="gray").pack()
        self.angle_light_azimuthal_entry = ttk.Combobox(
            root, textvariable=self.angle_light_azimuthal_var,
            values=angle_options, state="readonly"
        )
        self.angle_light_azimuthal_entry.pack()
        self.n_light_azimuthal_var = tk.StringVar()
        ttk.Label(root, textvariable=self.n_light_azimuthal_var, foreground="gray").pack()
        self.angle_light_azimuthal_entry.bind("<<ComboboxSelected>>", self.update_image_counts)

        # ---- Light Source Radial ----
        self.angle_light_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Light Source Radial Increment (°):").pack(pady=5)
        ttk.Label(root, text=self.range_label_text, foreground="gray").pack()
        self.angle_light_radial_entry = ttk.Combobox(
            root, textvariable=self.angle_light_radial_var,
            values=angle_options, state="readonly"
        )
        self.angle_light_radial_entry.pack()
        self.n_light_radial_var = tk.StringVar()
        ttk.Label(root, textvariable=self.n_light_radial_var, foreground="gray").pack()
        self.angle_light_radial_entry.bind("<<ComboboxSelected>>", self.update_image_counts)

        # ---- Detector Azimuthal ----
        self.angle_detector_azimuthal_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Azimuthal Increment (°):").pack(pady=5)
        ttk.Label(root, text=self.range_label_text, foreground="gray").pack()
        self.angle_detector_azimuthal_entry = ttk.Combobox(
            root, textvariable=self.angle_detector_azimuthal_var,
            values=angle_options, state="readonly"
        )
        self.angle_detector_azimuthal_entry.pack()
        self.n_detector_azimuthal_var = tk.StringVar()
        ttk.Label(root, textvariable=self.n_detector_azimuthal_var, foreground="gray").pack()
        self.angle_detector_azimuthal_entry.bind("<<ComboboxSelected>>", self.update_image_counts)

        # ---- Detector Radial ----
        self.angle_detector_radial_var = tk.DoubleVar()
        ttk.Label(root, text="Detector Radial Increment (°):").pack(pady=5)
        ttk.Label(root, text=self.range_label_text, foreground="gray").pack()
        self.angle_detector_radial_entry = ttk.Combobox(
            root, textvariable=self.angle_detector_radial_var,
            values=angle_options, state="readonly"
        )
        self.angle_detector_radial_entry.pack()
        self.n_detector_radial_var = tk.StringVar()
        ttk.Label(root, textvariable=self.n_detector_radial_var, foreground="gray").pack()
        self.angle_detector_radial_entry.bind("<<ComboboxSelected>>", self.update_image_counts)

        # Navigation Buttons
        ttk.Button(root, text="Next", command=self.next_window).pack(pady=20)
        self.back_button = ttk.Button(root, text="Back", command=self.go_back)
        self.back_button.pack(pady=5)

    def update_image_counts(self, event=None):
        """Update the number of steps for each increment based on the fixed range."""
        try:
            def calc(var):
                return f"→ Number of positions: {int(self.fixed_range / var.get()) + 1}" if var.get() else ""

            self.n_light_azimuthal_var.set(calc(self.angle_light_azimuthal_var))
            self.n_light_radial_var.set(calc(self.angle_light_radial_var))
            self.n_detector_azimuthal_var.set(calc(self.angle_detector_azimuthal_var))
            self.n_detector_radial_var.set(calc(self.angle_detector_radial_var))
        except Exception:
            pass

    def next_window(self):
        """Close the current window and open the Automation Controls window."""
        if (
            self.material_var.get().strip() == "" or
            self.angle_light_azimuthal_var.get() == 0.0 or
            self.angle_light_radial_var.get() == 0.0 or
            self.angle_detector_azimuthal_var.get() == 0.0 or
            self.angle_detector_radial_var.get() == 0.0
        ):
            messagebox.showwarning("Missing Input", "Please fill in all measurement parameters before continuing.")
            return
        
        self.root.destroy()
        new_root = tk.Tk()
        AutomationControlsWindow(new_root, self.measurement_type, self.get_parameters())
        new_root.mainloop()

    def go_back(self):
        """Go back to the Measurement Type window."""
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
            "fixed_range": self.fixed_range
        }
