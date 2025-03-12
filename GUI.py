import tkinter as tk
from tkinter import Label, Button, StringVar
from picamera2 import Picamera2
import time

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

# Function to capture RAW data
def capture_image():
    status_var.set("Capturing Image...")
    root.update_idletasks()  # Update UI

    picam2.start()
    time.sleep(1)  # Allow camera to stabilize

    file_name = "image.dng"
    picam2.capture_file(file_name, name="raw")
    picam2.stop()

    status_var.set(f"Image saved: {file_name}")

# Create main GUI window
root = tk.Tk()
root.title("Optical Scattering Measurement")
root.geometry("400x200")

# UI Elements
status_var = StringVar()
status_var.set("Press 'Capture Image' to start")

Label(root, text="BSDF Data Capture", font=("Arial", 14)).pack(pady=10)
Label(root, textvariable=status_var, font=("Arial", 12), fg="blue").pack(pady=5)

capture_button = Button(root, text="Capture Image", font=("Arial", 12), command=capture_image)
capture_button.pack(pady=10)

# Run the Tkinter loop
root.mainloop()






