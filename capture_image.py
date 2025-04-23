import os
import time
import numpy as np
from motors import Motors  
from process_image import extract_color_channels

def capture_raw_image(picam2):
    """Capture a raw Bayer image and save it as a 2D array."""
    try:
        # Capture the raw Bayer array and view it as 16-bit values
        raw_array = picam2.capture_array("raw").view(np.uint16)
        return raw_array

    except Exception as e:
        print(f"Failed to capture RAW image: {e}")
        return None

def check_and_adjust_exposure(picam2, image, target_max=972, tolerance=10, exposure_step=50):
    """
    Adjust exposure time based on the brightest channel in a raw Bayer image.
    Prioritizes the channel with the highest intensity to avoid clipping.
    """
    if image is None or picam2 is None:
        print("Invalid input to exposure check.")
        return False

    # Extract RGB channels
    R, G, B = extract_color_channels(image)

    # Compute max values per channel
    max_values = {'R': R.max(), 'G': G.max(), 'B': B.max()}
    priority_channel = max(max_values, key=max_values.get)
    priority_value = max_values[priority_channel]

    print(f"Max R: {max_values['R']}, Max G: {max_values['G']}, Max B: {max_values['B']}")
    print(f"Prioritizing channel: {priority_channel} (value: {priority_value})")

    # Get current exposure time from metadata (fallback to 10000 µs)
    metadata = picam2.capture_metadata()
    current_exp = metadata.get("ExposureTime", 10000)

    # Check if within acceptable range
    if target_max - tolerance <= priority_value <= target_max + tolerance:
        print("Exposure is acceptable.")
        return True

    # Adjust exposure time based on priority channel
    if priority_value > target_max + tolerance:
        new_exp = max(current_exp - exposure_step, 100)
        print("Too bright → Decreasing exposure")
    else:
        new_exp = current_exp + exposure_step
        print("Too dark → Increasing exposure")

    print(f"Adjusting exposure: {current_exp} → {new_exp}")
    picam2.set_controls({"ExposureTime": int(new_exp)})
    time.sleep(1)  # Give camera time to apply settings

    return False

def run_full_measurement(app, fixed_range=20, image_count=10, save_dir="Captured_Data"):
    picam2 = app.camera
    dark_value = app.dark_value

    if picam2 is None or dark_value is None:
        app.set_status("Camera or dark value not set.", "error")
        return

    os.makedirs(save_dir, exist_ok=True)

    ls_az_step = app.ls_az_step
    ls_rad_step = app.ls_rad_step
    det_az_step = app.det_az_step
    det_rad_step = app.det_rad_step

    light_az_steps = int(fixed_range / max(ls_az_step, 1))
    light_rad_steps = int(fixed_range / max(ls_rad_step, 1))
    det_az_steps = int(fixed_range / max(det_az_step, 1))
    det_rad_steps = int(fixed_range / max(det_rad_step, 1))

    motors = Motors()
    motors.move_light_to_offset()
    motors.move_detector_to_offset()

    capture_index = 1

    for laz_i in range(light_az_steps):
        if check_stop(app): return
        light_az = laz_i * ls_az_step
        motors.move_light_azimuthal(light_az)

        for lrad_i in range(light_rad_steps):
            if check_stop(app): return
            light_rad = lrad_i * ls_rad_step
            motors.move_light_radial(light_rad)

            for daz_i in range(det_az_steps):
                if check_stop(app): return
                det_az = daz_i * det_az_step

                for drad_i in range(det_rad_steps):
                    if check_stop(app): return
                    det_rad = drad_i * det_rad_step

                    motors.move_detector_azimuthal(det_az)
                    motors.move_detector_radial(det_rad)
                    time.sleep(0.5)

                    for attempt in range(10):
                        if check_stop(app): return
                        test_image = capture_raw_image(picam2)
                        if test_image is None:
                            continue
                        if check_and_adjust_exposure(picam2, test_image, dark_value):
                            break
                    else:
                        print("Exposure tuning failed, skipping this position.")
                        continue

                    for rep in range(image_count):
                        if check_stop(app): return
                        img = capture_raw_image(picam2)
                        if img is None:
                            print(f"Image {rep+1} failed.")
                            continue

                        corrected = np.clip(img.astype(np.float32) - dark_value, 0, None)
                        exposure = picam2.capture_metadata().get("ExposureTime", None)

                        filename = (
                            f"img_{capture_index:04d}_"
                            f"Laz{light_az}_Lrad{light_rad}_"
                            f"Daz{det_az}_Drad{det_rad}_"
                            f"rep{rep+1}_exp{exposure}.npy"
                        )
                        np.save(os.path.join(save_dir, filename), corrected)
                        print(f"Saved {filename}")

                    capture_index += 1

            motors.move_detector_to_offset()
            time.sleep(1)

    print("Full measurement complete.")

def check_stop(app):
    if getattr(app, "stop_requested", True):
        return True
    return False

