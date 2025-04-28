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
    options = ["2", "5", "10", "100"]  # Options for angular step size (in degrees) -> add different options for light source
    step_labels= {}
    app.step_counts = {} 

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
        app.angle_inputs[key] = combobox

        # Label to show number of steps
        step_label = ttk.Label(grid, text="Total Steps: ?", width=15)
        step_label.grid(row=i, column=2, padx=5)
        step_labels[key] = step_label

        combobox.bind("<<ComboboxSelected>>", lambda e, k=key: update_step_label(app, k, step_labels[k]))

    ttk.Button(frame, text="Next", command=lambda: [
        save_step_settings(app),
        app.set_status("Measurement setup complete!", "success"),
        app.next_step()
    ]).pack(pady=10)

def update_step_label(app, key, label):
    """Updates number of steps and stores them in app.step_counts."""
    try:
        step_deg = float(app.angle_inputs[key].get())

        mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
        start, end = RANGE_MAP.get(mtype, (8, 175))

        count = int((end - start) / step_deg)
        label.config(text=f"Total Steps: {count}")

        # Store in app.step_counts
        app.step_counts[key] = count

    except Exception:
        label.config(text="Total Steps: ?")
        app.step_counts[key] = None  # Optional: store None for errors

def save_step_settings(app):
    """Store selected angle step sizes (as float) in app.angle_step_sizes."""
    app.angle_step_sizes = {}
    for key, combobox in app.angle_inputs.items():
        value = combobox.get()
        if not value:
            raise ValueError(f"Step size not selected for {key}")
        app.angle_step_sizes[key] = float(value)
    
    # Also generate angles here
    generate_angle_lists(app)

def generate_angle_lists(app):
    """Generate incidence, azimuthal, and radial angles based on selected step sizes."""
    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
    start_incidence, end_incidence = RANGE_MAP.get(mtype, (8, 175))

    # Light source - incidence angles (radial movements of light source)
    ls_rad_step = app.angle_step_sizes.get("ls_rad", 5)  # default 5 deg
    app.incidence_angles = [start_incidence + i * ls_rad_step for i in range(int((end_incidence - start_incidence) / ls_rad_step) + 1)]

    # Detector azimuth angles
    det_az_step = app.angle_step_sizes.get("det_az", 5)
    app.azimuth_angles = [i * det_az_step for i in range(int(360 / det_az_step))]

    # Detector radial angles
    det_rad_step = app.angle_step_sizes.get("det_rad", 5)
    app.radial_angles = [i * det_rad_step for i in range(int(90 / det_rad_step) + 1)]  # Usually 0–90 degrees for scattering
