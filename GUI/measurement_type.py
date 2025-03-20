import tkinter as tk
from tkinter import ttk
from GUI.measurement_parameters import MeasurementParametersWindow

class MeasurementTypeWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Measurement Type Selection")
        self.root.geometry("500x300")
        
        ttk.Label(root, text="Select Measurement Type", font=("Arial", 14, "bold")).pack(pady=20)

        self.measurement_type_var = tk.StringVar(value="both")  # Default to both
        
        ttk.Radiobutton(root, text="BRDF (Reflection Only)", variable=self.measurement_type_var, value="brdf").pack()
        ttk.Radiobutton(root, text="BTDF (Transmission Only)", variable=self.measurement_type_var, value="btdf").pack()
        ttk.Radiobutton(root, text="Both BRDF & BTDF", variable=self.measurement_type_var, value="both").pack()
        
        ttk.Button(root, text="Next", command=self.next_window).pack(pady=20)
    
    def next_window(self):
        # Destroy current window and open Measurement Parameters
        self.root.destroy()
        new_root = tk.Tk()
        MeasurementParametersWindow(new_root, self.measurement_type_var.get())
        new_root.mainloop()