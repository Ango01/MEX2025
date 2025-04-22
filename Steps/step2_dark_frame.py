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
        filename = "dark_frame.npy"
        filepath = capture_raw_image(app.camera, filename=filename)

        if filepath:
            # Optional: load the dark frame for in-memory use
            app.dark_frame = np.load(filepath)

            print(f"Shape: {app.dark_frame.shape}")
            print(f"Dtype: {app.dark_frame.dtype}")
            print(f"Size (pixels): {app.dark_frame.size}")
            print(f"Memory usage: {app.dark_frame.nbytes} bytes")
            print(f"Min/Max: {app.dark_frame.min()} / {app.dark_frame.max()}")

            app.set_status(f"Dark frame saved: {filepath}", "success")
            app.next_step()
        else:
            app.set_status("Failed to capture dark frame", "error")
    else:
        app.set_status("Camera not initialized!", "error")
