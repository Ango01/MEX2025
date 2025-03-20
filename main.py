import tkinter as tk
from GUI.measurement_type import MeasurementTypeWindow

def main():
    root = tk.Tk()
    root.title("Optical Scattering Measurement Device")
    root.geometry("500x400")
    
    # Open the first window for choosing measurement type
    MeasurementTypeWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()