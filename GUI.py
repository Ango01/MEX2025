import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import cv2
from PIL import Image, ImageTk
from RAW10_processing import process_raw10_image

class Raw10Viewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer & Processor")
        
        self.canvas = tk.Canvas(root, width=500, height=400, bg="gray")
        self.canvas.pack()
        
        self.btn_load = tk.Button(root, text="Load RAW10 Image", command=self.load_raw10)
        self.btn_load.pack(pady=10)
        
        self.btn_process = tk.Button(root, text="Process RAW10 Image", command=self.process_raw10)
        self.btn_process.pack(pady=10)
        
        self.raw10_file = None
        self.width = 1456  # Change based on your camera
        self.height = 1088  # Change based on your camera

    def load_raw10(self):
        file_path = filedialog.askopenfilename(filetypes=[("RAW10 files", "*.raw")])
        if file_path:
            self.raw10_file = file_path
            image_data = process_raw10_image(self.raw10_file, self.width, self.height)
            if image_data is not None:
                self.display_image(image_data)

    def display_image(self, image_array):
        image_8bit = (image_array / 256).astype(np.uint8)  # Convert to 8-bit for display
        img = Image.fromarray(image_8bit)
        img = img.resize((500, 400), Image.LANCZOS)  # Resize to fit canvas
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.create_image(250, 200, image=self.tk_img)
    
    def process_raw10(self):
        if not self.raw10_file:
            messagebox.showwarning("Warning", "No RAW10 file loaded!")
            return
        
        image_data = process_raw10_image(self.raw10_file, self.width, self.height)
        if image_data is not None:
            self.display_image(image_data)
            messagebox.showinfo("Success", "Processing complete! Image saved as processed_image.png")

if __name__ == "__main__":
    root = tk.Tk()
    app = Raw10Viewer(root)
    root.mainloop()
