from tkinter import ttk

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 4: Set Angle Step Increments").pack(anchor="w", pady=5)

    grid = ttk.Frame(frame)
    grid.pack()

    app.angle_inputs = {}
    options = ["2", "5", "10"]  # angular step options as strings

    labels = [
        ("Light Source - Azimuthal Step (°):", "ls_az"),
        ("Light Source - Radial Step (°):", "ls_rad"),
        ("Detector - Azimuthal Step (°):", "det_az"),
        ("Detector - Radial Step (°):", "det_rad")
    ]

    for i, (label, key) in enumerate(labels):
        ttk.Label(grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)

        combobox = ttk.Combobox(grid, values=options, width=8, state="readonly")
        combobox.set(options[0])  # Set default to 2°
        combobox.grid(row=i, column=1, padx=5, pady=2)

        app.angle_inputs[key] = combobox
    
    # Extract and store the values from comboboxes 
    app.ls_az_step = float(app.angle_inputs["ls_az"].get())
    app.ls_rad_step = float(app.angle_inputs["ls_rad"].get())
    app.det_az_step = float(app.angle_inputs["det_az"].get())
    app.det_rad_step = float(app.angle_inputs["det_rad"].get())

    ttk.Button(frame, text="Next", command=lambda: save_and_continue(app)).pack(pady=10)

def save_and_continue(app):
    try:
        app.ls_az_step = float(app.angle_inputs["ls_az"].get())
        app.ls_rad_step = float(app.angle_inputs["ls_rad"].get())
        app.det_az_step = float(app.angle_inputs["det_az"].get())
        app.det_rad_step = float(app.angle_inputs["det_rad"].get())
        app.set_status("Measurement setup complete!", "success")
        app.next_step()
    except Exception as e:
        app.set_status(f"Invalid input: {e}", "error")

