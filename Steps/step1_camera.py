from tkinter import ttk
from camera import initialize_camera

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 1: Initialize Camera").pack(anchor="w", pady=5)
    ttk.Button(frame, text="Start Camera", command=lambda:start_camera(app)).pack(pady=10)

def start_camera(app):
    camera = initialize_camera()
    if camera:
        app.camera = camera  # Store the instance in the main app for future use
        app.set_status("Camera ready", "success")
        app.next_step()
    else:
        app.set_status("Failed to initialize camera", "error")
