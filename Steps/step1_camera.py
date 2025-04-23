from tkinter import ttk
from camera import initialize_camera

def create(app, container):
    """Create function for Step 1: Camera Initialization."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 1: Initialize Camera").pack(anchor="w", pady=5)
    ttk.Button(frame, text="Start Camera", command=lambda:start_camera(app)).pack(pady=10)

def start_camera(app):
    """This function is called when "Start Camera" button is clicked."""
    camera = initialize_camera()

    if camera:
        app.camera = camera  # Save camera object in the main app for later use
        app.set_status("Camera ready", "success")
        app.next_step()
    else:
        app.set_status("Failed to initialize camera", "error")
