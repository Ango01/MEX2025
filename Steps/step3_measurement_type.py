from tkinter import ttk
import tkinter as tk

def create(app, container):
    """Create function for Step 3: Select measurement type."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 3: Select Measurement Type").pack(anchor="w", pady=5)

    # Store the selected measurement type
    app.measurement_type = tk.StringVar()
    
    options = ttk.Frame(frame)
    options.pack(pady=5)

    ttk.Radiobutton(options, text="BRDF", variable=app.measurement_type, value="BRDF").grid(row=0, column=0, padx=10)
    ttk.Radiobutton(options, text="BTDF", variable=app.measurement_type, value="BTDF").grid(row=0, column=1, padx=10)
    ttk.Radiobutton(options, text="Both", variable=app.measurement_type, value="Both").grid(row=0, column=2, padx=10)

    ttk.Button(frame, text="Next", command=lambda: [
        app.set_status(f"Measurement type selected: {app.measurement_type.get()}", "success"),
        app.next_step()
    ]).pack(pady=10)
