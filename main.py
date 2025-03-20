import tkinter as tk
from GUI import measurement_type

def main():
    root = tk.Tk()
    root.title("Optical Scattering Measurement Device")
    root.geometry("500x400")
    
    # Open the first window for choosing measurement type
    measurement_type.MeasurementTypeWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()