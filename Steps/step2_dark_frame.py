from tkinter import ttk

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 2: Dark Frame Setup").pack(anchor="w", pady=5)

    options = ttk.Frame(frame)
    options.pack(pady=5)

    ttk.Button(options, text="Capture Dark Frame", command=lambda: [
        app.set_status("Dark frame captured", "success"),
        app.next_step()
    ]).grid(row=0, column=0, padx=5)

    manual = ttk.Frame(options)
    manual.grid(row=0, column=1, padx=5)

    ttk.Label(manual, text="Or enter nominal value:").pack(anchor="w")
    entry = ttk.Entry(manual, width=12)
    entry.pack()
