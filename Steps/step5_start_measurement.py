from tkinter import ttk
from capture_image import capture_raw_image, check_and_adjust_exposure

def create(app, container):
    frame = ttk.Frame(container)
    frame.pack(fill="both", expand=True)

    ttk.Label(frame, text="Step 5: Start Measurement").pack(anchor="w", pady=10)

    ttk.Label(
        frame,
        text="Click the button below to start the measurement process."
    ).pack(anchor="w", pady=5)

    ttk.Button(
        frame,
        text="Start",
        command=lambda: start_measurement(app)
    ).pack(pady=15)

def start_measurement(app):
    if not hasattr(app, "camera") or app.camera is None:
        app.set_status("Camera not initialized.", "error")
        return

    if not hasattr(app, "dark_value"):
        app.set_status("Dark value missing. Capture or enter it first.", "error")
        return

    app.set_status("Tuning exposure...", "info")
    picam2 = app.camera
    MAX_ATTEMPTS = 10
    SHAPE = (1088, 1456)

    # Step 1: Exposure tuning loop
    for attempt in range(MAX_ATTEMPTS):
        test_image = capture_raw_image(picam2, shape=SHAPE)
        if test_image is None:
            app.set_status("Failed to capture test image.", "error")
            return

        if check_and_adjust_exposure(picam2, test_image, app.dark_value):
            app.set_status("Exposure tuned. Capturing images...", "success")
            break
    else:
        app.set_status("Exposure tuning failed after 10 attempts.", "warning")
        return

    # Step 2: Capture 10 corrected images + exposure time
    images_with_exposure = []

    for i in range(10):
        image = capture_raw_image(picam2, shape=SHAPE)
        if image is not None:
            metadata = picam2.capture_metadata()
            exposure_time = metadata.get("ExposureTime", None)

            images_with_exposure.append({
                "image": image,
                "exposure_time": exposure_time
            })

            print(f"Captured image {i+1}/10 — Exposure: {exposure_time} µs")
        else:
            print(f"Image {i+1} failed.")

    app.measurement_images = images_with_exposure
    app.set_status(f"Captured {len(images_with_exposure)} images with exposure times.", "info")

    for entry in app.measurement_images:
        print(entry["exposure_time"], entry["image"].shape)
        
