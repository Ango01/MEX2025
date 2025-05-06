from tkinter import ttk

# Angle ranges based on measurement type
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

    angle_inputs = {}
    step_labels = {}
    options = ["2", "5", "10", "100"]  # Light source + detector step size options

    labels = [
        ("Light Source - Azimuthal Step (°):", "ls_az"),
        ("Light Source - Radial Step (°):", "ls_rad"),
        ("Detector - Azimuthal Step (°):", "det_az"),
        ("Detector - Radial Step (°):", "det_rad")
    ]

    for i, (label, key) in enumerate(labels):
        ttk.Label(grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)

        combobox = ttk.Combobox(grid, values=options, width=8, state="readonly")
        combobox.grid(row=i, column=1, padx=5, pady=2)
        angle_inputs[key] = combobox

        # Label to show number of steps
        step_label = ttk.Label(grid, text="Steps: ?", width=15)
        step_label.grid(row=i, column=2, padx=5)
        step_labels[key] = step_label

        # Bind selection change
        combobox.bind("<<ComboboxSelected>>", lambda e, k=key: update_step_label(app, angle_inputs, k, step_labels[k]))

    nav_buttons = ttk.Frame(frame)
    nav_buttons.pack(pady=10)

    ttk.Button(nav_buttons, text="Back", command=lambda: app.show_step(3)).pack(side="left", padx=5)
    ttk.Button(nav_buttons, text="Next", command=lambda: (
    app.set_status("Please select all angle step sizes before continuing.", "error")
    if any(not cb.get() for cb in angle_inputs.values())
    else (save_step_settings(app, angle_inputs), app.set_status("Measurement setup complete!", "success"), app.next_step())
)).pack(side="left", padx=5)

def update_step_label(app, angle_inputs, key, label):
    """Updates number of steps and stores them in app.step_counts."""
    try:
        step_deg = float(angle_inputs[key].get())

        mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        start, end = RANGE_MAP.get(mtype, (8, 175))

        count = int((end - start) / step_deg) + 1
        label.config(text=f"Steps: {count}")

    except Exception:
        label.config(text="Steps: ?")

def save_step_settings(app, angle_inputs):
    """Store selected angle step sizes and generate angle lists."""
    app.angle_step_sizes = {}
    for key, combobox in angle_inputs.items():
        value = combobox.get()
        if not value:
            raise ValueError(f"Step size not selected for {key}")
        app.angle_step_sizes[key] = float(value)

    generate_angle_lists(app)

def generate_angle_lists(app):
    """Generate incidence, azimuthal, and radial angles based on selected step sizes."""
    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
    start, end = RANGE_MAP.get(mtype, (8, 175))

    # Light Source - Azimuthal (Incidence)
    ls_az_step = app.angle_step_sizes.get("ls_az", 5)
    app.incidence_angles = [angle for angle in range(start, end + 1, int(ls_az_step))]

    # Light Source - Radial (Sample Rotation)
    ls_rad_step = app.angle_step_sizes.get("ls_rad", 5)
    app.light_radial_angles = [angle for angle in range(start, end + 1, int(ls_rad_step))]

    # Detector - Azimuthal
    det_az_step = app.angle_step_sizes.get("det_az", 5)
    app.det_azimuth_angles = [angle for angle in range(start, end + 1, int(det_az_step))]

    # Detector - Radial
    det_rad_step = app.angle_step_sizes.get("det_rad", 5)
    app.det_radial_angles = [angle for angle in range(start, end + 1, int(det_rad_step))]

