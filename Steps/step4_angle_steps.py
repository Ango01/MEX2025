from tkinter import ttk

RANGE_MAP = {
    "BRDF": (8, 175),
    "BTDF": (188, 355),
    "Both": (8, 355),
}

def create(app, container):
    """Create function for Step 4: Angle step size selection."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 4: Set Angle Step Increments").pack(anchor="w", pady=5)

    grid = ttk.Frame(frame)
    grid.pack()

    app.angle_inputs = {}
    options = ["2", "5", "10"]  # Options for angular step size (in degrees) -> add different options for light source
    step_labels = {} 

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

        # Label to show number of steps
        step_label = ttk.Label(grid, text="Steps: ?", width=15)
        step_label.grid(row=i, column=2, padx=5)
        step_labels[key] = step_label

        combobox.bind("<<ComboboxSelected>>", lambda e, k=key: update_step_label(app, k, step_labels[k]))

    ttk.Button(frame, text="Next", command=lambda: save_and_continue(app)).pack(pady=10)

def save_and_continue(app):
    """Function to store selected values."""
    try:
        app.ls_az_step = float(app.angle_inputs["ls_az"].get())
        app.ls_rad_step = float(app.angle_inputs["ls_rad"].get())
        app.det_az_step = float(app.angle_inputs["det_az"].get())
        app.det_rad_step = float(app.angle_inputs["det_rad"].get())

        app.set_status("Measurement setup complete!", "success")
        app.next_step()
    except Exception as e:
        app.set_status(f"Invalid input: {e}", "error")

def update_step_label(app, key, label):
    """Updates number of steps taken at each direction depending on the step size chosen."""
    try:
        step_deg = float(app.angle_inputs[key].get())

        # Get measurement type and corresponding angular range
        mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        start, end = RANGE_MAP.get(mtype, (8, 175))

        # Calculate number of steps
        count = int((end - start) / step_deg)
        label.config(text=f"Steps: {count}")
    except Exception:
        label.config(text="Steps: ?")


