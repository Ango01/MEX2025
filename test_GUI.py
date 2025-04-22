import tkinter as tk
from tkinter import ttk

class ScatteringApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Optical Scattering Measurement")
        self.geometry("600x300")
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
        self.style.theme_use("clam")
        font = ("Helvetica Neue", 11)

        self.style.configure("TButton", font=font, padding=6, foreground="#ffffff", background="#0059b3")
        self.style.map("TButton", background=[("active", "#004080")])
        self.style.configure("TLabel", font=font, padding=2)
        self.style.configure("TEntry", font=font, padding=2)
        self.style.configure("TRadiobutton", font=font)

    def create_status_bar(self):
        self.status_frame = tk.Frame(self, height=30, bg="#e0e0e0")
        self.status_frame.pack(side="bottom", fill="x")

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(self.status_frame, textvariable=self.status_var,
                                     font=("Helvetica Neue", 10, "bold"),
                                     bg="#e0e0e0", fg="#000000", anchor="w", padx=10)
        self.status_label.pack(fill="x")
        self.set_status("Ready", "neutral")

    def set_status(self, message, status_type="neutral"):
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
        for widget in self.step_container.winfo_children():
            widget.destroy()
        if 0 <= index < len(self.steps):
            self.steps[index](self.step_container)
            self.current_step = index

    def next_step(self):
        self.show_step(self.current_step + 1)

    def create_steps(self):
        self.steps = [
            self.step1_camera,
            self.step2_dark_frame,
            self.step3_measurement_type,
            self.step4_angle_steps
        ]

    # ----------- STEP 1 ------------
    def step1_camera(self, container):
        frame = ttk.Frame(container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Step 1: Initialize Camera").pack(anchor="w", pady=5)
        ttk.Button(frame, text="Start Camera", command=lambda: [
            self.set_status("Camera started!", "success"),
            self.next_step()
        ]).pack(pady=10)

    # ----------- STEP 2 ------------
    def step2_dark_frame(self, container):
        frame = ttk.Frame(container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Step 2: Dark Frame Setup").pack(anchor="w", pady=5)

        options = ttk.Frame(frame)
        options.pack(pady=5)

        ttk.Button(options, text="Capture Dark Frame", command=lambda: [
            self.set_status("Dark frame captured", "success"),
            self.next_step()
        ]).grid(row=0, column=0, padx=5)

        manual = ttk.Frame(options)
        manual.grid(row=0, column=1, padx=5)

        ttk.Label(manual, text="Or enter nominal value:").pack(anchor="w")
        entry = ttk.Entry(manual, width=12)
        entry.pack()

    # ----------- STEP 3 ------------
    def step3_measurement_type(self, container):
        frame = ttk.Frame(container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Step 3: Select Measurement Type").pack(anchor="w", pady=5)

        self.measurement_type = tk.StringVar()
        options = ttk.Frame(frame)
        options.pack(pady=5)

        ttk.Radiobutton(options, text="BRDF", variable=self.measurement_type, value="BRDF").grid(row=0, column=0, padx=10)
        ttk.Radiobutton(options, text="BTDF", variable=self.measurement_type, value="BTDF").grid(row=0, column=1, padx=10)
        ttk.Radiobutton(options, text="Both", variable=self.measurement_type, value="Both").grid(row=0, column=2, padx=10)

        ttk.Button(frame, text="Next", command=lambda: [
            self.set_status(f"Measurement type selected: {self.measurement_type.get()}", "info"),
            self.next_step()
        ]).pack(pady=10)

    # ----------- STEP 4 ------------
    def step4_angle_steps(self, container):
        frame = ttk.Frame(container)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Step 4: Set Angle Step Increments").pack(anchor="w", pady=5)

        grid = ttk.Frame(frame)
        grid.pack()

        self.angle_inputs = {}
        labels = [
            ("Light Source - Azimuthal Step (°):", "ls_az"),
            ("Light Source - Radial Step (°):", "ls_rad"),
            ("Detector - Azimuthal Step (°):", "det_az"),
            ("Detector - Radial Step (°):", "det_rad")
        ]

        for i, (label, key) in enumerate(labels):
            ttk.Label(grid, text=label).grid(row=i, column=0, sticky="w", padx=5, pady=2)
            entry = ttk.Entry(grid, width=10)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.angle_inputs[key] = entry

        ttk.Button(frame, text="Finish", command=lambda: self.set_status("Measurement setup complete!", "success")).pack(pady=10)

if __name__ == "__main__":
    app = ScatteringApp()
    app.mainloop()