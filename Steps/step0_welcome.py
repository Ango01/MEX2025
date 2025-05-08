from tkinter import ttk

def create(app, container):
    """Create function for Step 0: Welcome screen."""
    # Create a frame to hold all widgets for this step
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    # Main welcome message
    ttk.Label(
        frame,
        text="Welcome to the Optical Scattering Measurement System",
        font=("Helvetica", 14, "bold")
    ).pack(pady=20)

    ttk.Label(
        frame,
        text="Click 'Next' to begin the setup process.",
    ).pack(pady=10)
    
    # Next button to proceed to the next step
    ttk.Button(
        frame,
        text="Next",
        command=app.next_step
    ).pack(pady=20)
