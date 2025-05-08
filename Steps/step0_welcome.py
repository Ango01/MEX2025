import logging, sys, os
from datetime import datetime
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

    # Create a "Logs" directory
    os.makedirs("Logs", exist_ok=True)

    # Generate timestamped filename
    log_filename = datetime.now().strftime("Logs/measurement_%Y%m%d_%H%M%S.log")

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Replace all future print() calls with this:
    print = logging.info  # Redirect print to logging