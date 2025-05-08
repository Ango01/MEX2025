from tkinter import ttk
from camera import initialize_camera

def create(app, container):
    """Create function for Step 1: Camera Initialization."""
    # Create a frame to hold all widgets for this step
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    # Step label
    ttk.Label(frame, text="Step 1: Initialize Camera").pack(anchor="w", pady=5)

    # Button to start camera initialization
    ttk.Button(frame, text="Start Camera", command=lambda:start_camera(app)).pack(pady=10)

def start_camera(app):
    """Initialize the camera."""
    camera = initialize_camera()

    if camera:
        # Store the camera object in the main app and update the status
        app.camera = camera  
        app.set_status("Camera ready", "success")
        app.next_step()
    else:
        # If initialization failed, show error message
        app.set_status("Failed to initialize camera", "error")
