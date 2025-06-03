import logging, sys, os
from datetime import datetime
from app import ScatteringApp

if __name__ == "__main__":
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

    # Start GUI application
    app = ScatteringApp()
    app.mainloop()