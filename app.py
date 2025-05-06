import tkinter as tk
from tkinter import ttk
from Steps import step0_welcome, step1_camera, step2_dark_frame, step3_measurement_type, step4_angle_steps, step5_start_measurement

# Main application class
class ScatteringApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.title("Optical Scattering Measurement")
        self.geometry("600x350")
        self.configure(bg="#f0f2f5")

        self.style = ttk.Style(self)
        self.set_style()

        self.current_step = 0
        self.steps = [] 

        self.step_container = ttk.Frame(self)
        self.step_container.pack(fill="both", expand=True, padx=20, pady=10)

        self.create_status_bar()
        self.create_steps()
        self.show_step(0)

    def set_style(self):
        """Set up the application's visual style."""
        self.style.theme_use("clam")
        font = ("Helvetica Neue", 11)

        self.style.configure("TButton", font=font, padding=6, foreground="#ffffff", background="#0059b3")
        self.style.map("TButton", background=[("active", "#004080")])
        self.style.configure("TLabel", font=font, padding=2)
        self.style.configure("TEntry", font=font, padding=2)
        self.style.configure("TRadiobutton", font=font)

    def create_status_bar(self):
        """Create the bottom status bar to show messages."""
        self.status_frame = tk.Frame(self, bg="#e0e0e0")
        self.status_frame.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                                     font=("Helvetica Neue", 11, "bold"),
                                     bg="#e0e0e0", fg="#000000", anchor="w", padx=10, pady=10)
        self.status_label.pack(fill="x")

        # Set initial status
        self.set_status("Welcome!", "info")

    def set_status(self, message, status_type="neutral"):
        """Update the status message and style based on type."""
        colors = {
            "neutral": ("#e0e0e0", "#000000"),
            "info": ("#d9edf7", "#31708f"),
            "success": ("#dff0d8", "#3c763d"),
            "warning": ("#fcf8e3", "#8a6d3b"),
            "error": ("#f2dede", "#a94442"),
        }
        bg, fg = colors.get(status_type, ("#e0e0e0", "#000000"))
        self.status_var.set(message)
        self.status_label.config(bg=bg, fg=fg)
        self.status_frame.config(bg=bg)

    def show_step(self, index):
        """Display a step UI, replacing the current view."""
        for widget in self.step_container.winfo_children():
            widget.destroy()
        if 0 <= index < len(self.steps):
            self.steps[index](self, self.step_container)
            self.current_step = index

    def next_step(self):
        """Go to the next step in the list."""
        self.show_step(self.current_step + 1)

    def create_steps(self):
        """Define the sequence of steps."""
        self.steps = [
            step0_welcome.create,
            step1_camera.create,
            step2_dark_frame.create,
            step3_measurement_type.create,
            step4_angle_steps.create,
            step5_start_measurement.create
        ]