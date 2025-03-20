import tkinter as tk
from GUI.measurement_type import MeasurementTypeWindow

def main():
    """Main function to create and launch the GUI application."""

    # Create the main application window
    root = tk.Tk()
    root.title("Optical Scattering Measurement Device")
    root.geometry("500x400")
    
    # Open the first window for choosing measurement type
    MeasurementTypeWindow(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()