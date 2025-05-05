from tkinter import ttk

def create(app, container):
    """Create function for Step 0: Welcome screen."""
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(
        frame,
        text="Welcome to the Optical Scattering Measurement System",
        font=("Helvetica", 14, "bold")
    ).pack(pady=20)

    ttk.Label(
        frame,
        text="Click 'Next' to begin the setup process.",
    ).pack(pady=10)

    ttk.Button(
        frame,
        text="Next",
        command=app.next_step
    ).pack(pady=20)
