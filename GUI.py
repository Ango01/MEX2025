import tkinter as tk
from tkinter import filedialog, Label, Button, Frame, messagebox
from PIL import Image, ImageTk
import cv2
import numpy as np
import image_processing  # Import your processing module

class BSDFApp:
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("BSDF Measurement GUI")
        self.root.geometry("800x600")  # Set default window size
        
        # Frame for UI layout
        self.frame = Frame(self.root)
        self.frame.pack(pady=20)

        # Label to display image
        self.label = Label(self.frame, text="No Image Loaded", width=60, height=20)
        self.label.pack()

        # Button to load an image
        self.load_button = Button(self.frame, text="Load Image", command=self.load_image)
        self.load_button.pack(pady=10)

        # Button to process the image
        self.process_button = Button(self.frame, text="Process Image", command=self.process_image)
        self.process_button.pack(pady=10)

        # Variable to hold the loaded image
        self.image = None

    def load_image(self):
        """Open a file dialog to load an image and display it."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.tif;*.raw")])
        
        if file_path:
            # Load image using OpenCV (grayscale)
            self.image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            if self.image is None:
                messagebox.showerror("Error", "Failed to load image.")
                return

            # Get original dimensions
            h, w = self.image.shape
            print(f"Original Image Size: {w}x{h}")

            # Resize for display
            label_w, label_h = 600, 400
            scale = min(label_w / w, label_h / h)
            new_w, new_h = int(w * scale), int(h * scale)

            image_resized = cv2.resize(self.image, (new_w, new_h), interpolation=cv2.INTER_AREA)
            image_pil = Image.fromarray(image_resized)
            image_tk = ImageTk.PhotoImage(image_pil)

            # Update label with image
            self.label.config(image=image_tk, text="", width=new_w, height=new_h)
            self.label.image = image_tk  # Keep reference to avoid garbage collection

            print(f"Displayed Image Size: {new_w}x{new_h}")

    def process_image(self):
        """Process the loaded image using external functions from image_processing.py"""
        if self.image is None:
            messagebox.showwarning("Warning", "Please load an image before processing.")
            return

        # Preprocess the image
        processed_image = image_processing.preprocess_image(self.image)
        
        # Compute BSDF value
        bsdf_value = image_processing.compute_bsdf(processed_image)

        # Show BSDF result
        messagebox.showinfo("BSDF Computation", f"BSDF Value: {bsdf_value:.4f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = BSDFApp(root)
    root.mainloop()