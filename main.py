import tkinter as tk
from tkinter import ttk
from GUI.measurement_type import MeasurementTypeWindow

def main():
    """Main function to create and launch the GUI application with a welcome screen."""
    global welcome_root
    welcome_root = tk.Tk()
    welcome_root.title("Welcome")
    welcome_root.geometry("500x250")

    ttk.Label(welcome_root, text="Welcome to the Optical Scattering Measurement Device",
              font=("Arial", 14, "bold"), wraplength=400, justify="center").pack(pady=60)
    
    ttk.Button(welcome_root, text="Start", command=next_window).pack()

    welcome_root.mainloop()

def next_window():
    """Open Measurement Type window."""
    welcome_root.destroy()
    root = tk.Tk()
    MeasurementTypeWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()