import tkinter as tk
from tkinter import filedialog, Label, Button, Frame
from PIL import Image, ImageTk
import cv2
import numpy as np

class BSDFApp:
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("BSDF Measurement GUI")
        self.root.geometry("800x600")  # Set default window size
        
        # Frame for UI Layout
        self.frame = Frame(self.root)
        self.frame.pack(pady=20)

        # Label to display image
        self.label = Label(self.frame, text="No Image Loaded", width=60, height=20)
        self.label.pack()

        # Load Image Button
        self.load_button = Button(self.frame, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        # Process Image Button (Placeholder for BSDF computation)
        self.process_button = Button(self.frame, text="Process Image", command=self.process_image)
        self.process_button.pack(pady=10)

    def load_image(self):
        """Opens a file dialog to load an image and displays it."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tif;*.raw")])
        
        if file_path:
            # Load image using OpenCV
            image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            
            # Resize image for display in the GUI
            image_resized = cv2.resize(image, (400, 400))
            
            # Convert to PIL format for Tkinter
            image_pil = Image.fromarray(image_resized)
            image_tk = ImageTk.PhotoImage(image_pil)

            # Update label with image
            self.label.config(image=image_tk)
            self.label.image = image_tk  # Keep a reference

            print(f"Loaded Image: {file_path}")

    def process_image(self):
        """Placeholder function for image processing."""
        print("Processing Image... (Feature to be added)")
        # This function can be expanded to process BSDF calculations.

if __name__ == "__main__":
    root = tk.Tk()
    app = BSDFApp(root)
    root.mainloop()
