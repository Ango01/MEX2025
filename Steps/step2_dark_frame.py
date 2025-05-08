from tkinter import ttk
from capture_image import capture_raw_image

def create(app, container):
    """Create function for Step 2: Capture or enter a dark frame."""
    # Create frame for this step
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)
    
    # Step title
    ttk.Label(frame, text="Step 2: Dark Frame").pack(anchor="w", pady=5)
    ttk.Label(frame, text="Capture dark frame with light source off or enter nominal value.").pack(anchor="w", pady=5)

    # Frame to hold capture and manual input options side by side
    options = ttk.Frame(frame)
    options.pack(pady=5)

    # Button to capture dark frame using camera (requires light source off)
    ttk.Button(options, text="Capture Dark Frame", command=lambda: capture_dark_frame(app)).grid(row=0, column=0, padx=5)

    # Manual entry section for nominal dark value
    manual = ttk.Frame(options)
    manual.grid(row=0, column=1, padx=5)

    ttk.Label(manual, text="Nominal Value: ").pack(anchor="w")
    entry = ttk.Entry(manual, width=12)
    entry.pack()

    # Button to apply manual value
    ttk.Button(manual, text="Use Value", command=lambda: set_nominal_dark_value(app, entry)).pack(pady=5)

def capture_dark_frame(app):
    """Capture dark frame using the camera and store its mean."""
    # Check that the camera is initialized
    if hasattr(app, "camera") and app.camera:
        dark_frame = capture_raw_image(app.camera)

        if dark_frame is not None:
            # Store mean intensity of dark frame
            app.dark_value = dark_frame.mean()

            # Debug info in console
            print(f"Shape: {dark_frame.shape}")
            print(f"Dtype: {dark_frame.dtype}")
            print(f"Size (pixels): {dark_frame.size}")
            print(f"Min/Max: {dark_frame.min()} / {dark_frame.max()}")
            print(f"Mean intensity (dark_value): {app.dark_value:.2f}")

            # Update status and proceed to next step
            app.set_status(f"Dark frame captured - Mean value: {app.dark_value:.2f}", "success")
            app.next_step()
        else:
            app.set_status("Failed to capture dark frame", "error")
    else:
        app.set_status("Camera not initialized!", "error")
        app.show_step(1) # Redirect to Step 1

def set_nominal_dark_value(app, entry):
    """Use manually entered nominal dark value."""
    try:
        value = float(entry.get()) # Convert input text to float
        app.dark_value = value

        app.set_status(f"Nominal dark value set: {app.dark_value:.2f}", "success")
        app.next_step()

    except ValueError:
         # Handle invalid input
        app.set_status("Invalid nominal value entered", "error")

