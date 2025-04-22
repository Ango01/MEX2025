from tkinter import ttk
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
        filepath = capture_raw_image(app.camera, filename="dark_frame.bin")
        import os
        size_bytes = os.path.getsize("dark_frame.bin")
        print(f"File size: {size_bytes} bytes")
        import numpy as np

        width, height = 1456, 1088

        with open("dark_frame.bin", "rb") as f:
            raw_data = np.frombuffer(f.read(), dtype=np.uint16)

        # Check total number of values
        print(f"Total pixels: {raw_data.size}")
        print(f"Expected: {width * height}")
        print(f"Dtype: {raw_data.dtype}")
        if filepath:
            app.set_status(f"Dark frame saved: {filepath}", "success")
            app.next_step()
        else:
            app.set_status("Failed to capture dark frame", "error")
    else:
        app.set_status("Camera not initialized!", "error")
