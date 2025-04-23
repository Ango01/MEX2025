from tkinter import ttk
from capture_image import capture_raw_image

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 2: Dark Frame").pack(anchor="w", pady=5)
    ttk.Label(frame, text="Capture dark frame with light source off or enter nominal value.").pack(anchor="w", pady=5)

    options = ttk.Frame(frame)
    options.pack(pady=5)

    # Button to capture dark frame
    ttk.Button(options, text="Capture Dark Frame", command=lambda: capture_dark_frame(app)).grid(row=0, column=0, padx=5)

    # Optional manual input
    manual = ttk.Frame(options)
    manual.grid(row=0, column=1, padx=5)

    ttk.Label(manual, text="Nominal Value: ").pack(anchor="w")
    entry = ttk.Entry(manual, width=12)
    entry.pack()

    # Button to use manual value
    ttk.Button(manual, text="Use Value", command=lambda: set_nominal_dark_value(app, entry)).pack(pady=5)

def capture_dark_frame(app):
    if hasattr(app, "camera") and app.camera:
        dark_frame = capture_raw_image(app.camera)

        if dark_frame is not None:
            app.dark_frame = dark_frame
            app.dark_value = dark_frame.mean()

            print(f"Shape: {dark_frame.shape}")
            print(f"Dtype: {dark_frame.dtype}")
            print(f"Size (pixels): {dark_frame.size}")
            print(f"Min/Max: {dark_frame.min()} / {dark_frame.max()}")
            print(f"Mean intensity (dark_value): {app.dark_value:.2f}")

            app.set_status(f"Dark frame captured - Mean value: {app.dark_value:.2f}", "success")
            app.next_step()
        else:
            app.set_status("Failed to capture dark frame", "error")
    else:
        app.set_status("Camera not initialized!", "error")

def set_nominal_dark_value(app, entry):
    try:
        value = float(entry.get())
        app.dark_frame = None  # No actual frame, just a value
        app.dark_value = value

        app.set_status(f"Nominal dark value set: {app.dark_value:.2f}", "success")
        app.next_step()

    except ValueError:
        app.set_status("Invalid nominal value entered", "error")

