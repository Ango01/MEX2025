from tkinter import ttk
import numpy as np
from capture_image import capture_raw_image

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 2: Dark Frame").pack(anchor="w", pady=5)

    options = ttk.Frame(frame)
    options.pack(pady=5)

    # Button to capture dark frame
    ttk.Button(options, text="Capture Dark Frame", command=lambda: capture_dark_frame(app)).grid(row=0, column=0, padx=5)

    # Optional manual input
    manual = ttk.Frame(options)
    manual.grid(row=0, column=1, padx=5)

    ttk.Label(manual, text="Or enter nominal value:").pack(anchor="w")
    entry = ttk.Entry(manual, width=12)
    entry.pack()

def capture_dark_frame(app):
    if hasattr(app, "camera") and app.camera:
        dark_frame = capture_raw_image(app.camera)

        if dark_frame is not None:
            app.dark_frame = dark_frame
            app.dark_value = dark_frame.mean()

            print(f"Shape: {dark_frame.shape}")
            print(f"Dtype: {dark_frame.dtype}")
            print(f"Size (pixels): {dark_frame.size}")
            print(f"Memory usage: {dark_frame.nbytes} bytes")
            print(f"Min/Max: {dark_frame.min()} / {dark_frame.max()}")
            print(f"Mean intensity (dark_value): {app.dark_value:.2f}")

            app.set_status("Dark frame captured and analyzed", "success")
            app.next_step()
        else:
            app.set_status("Failed to capture dark frame", "error")
    else:
        app.set_status("Camera not initialized!", "error")
