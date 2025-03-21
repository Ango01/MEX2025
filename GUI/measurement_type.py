import tkinter as tk
from tkinter import ttk, messagebox
from GUI.measurement_parameters import MeasurementParametersWindow

class MeasurementTypeWindow:
    """Class to create a window for selecting the measurement type."""
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Type Selection")
        self.root.geometry("500x250")
        
        ttk.Label(root, text="Select Measurement Type", font=("Arial", 14, "bold")).pack(pady=20)

        # Store the selected measurement type
        self.measurement_type_var = tk.StringVar(value="")  
        
        ttk.Radiobutton(root, text="BRDF (Reflection Only)", variable=self.measurement_type_var, value="brdf").pack(pady=5)
        ttk.Radiobutton(root, text="BTDF (Transmission Only)", variable=self.measurement_type_var, value="btdf").pack(pady=5)
        ttk.Radiobutton(root, text="Both BRDF & BTDF", variable=self.measurement_type_var, value="both").pack(pady=5)
        
        ttk.Button(root, text="Next", command=self.next_window).pack(pady=20)
    
    def next_window(self):
        """Closes the current window and opens the Measurement Parameters window."""
        if not self.measurement_type_var.get():  # Check if a selection has been made
            messagebox.showwarning("Selection Required", "Please select a measurement type before proceeding.")
            return
        
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementParametersWindow(new_root, self.measurement_type_var.get())
        new_root.mainloop()