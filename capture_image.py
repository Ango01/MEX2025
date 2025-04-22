import os
import json
import time
from datetime import datetime
from motors import Motors  
import process_image
import numpy as np

def capture_raw_image(picam2):
    """Capture a raw Bayer image and save it as a 2D array."""
    try:
        # Capture the raw Bayer array and view it as 16-bit values
        raw_array = picam2.capture_array("raw").view(np.uint16)
        return raw_array

    except Exception as e:
        print(f"Failed to capture RAW image: {e}")
        return None

def check_and_adjust_exposure(picam2, image,
                               target_mean=1000, tolerance=100,
                               exposure_step=1000):
    """
    Check exposure based on a single image and adjust if needed.

    Args:
        picam2: Initialized Picamera2 instance
        image: Raw 2D NumPy image from the sensor
        dark_value: Mean intensity of dark frame
        target_mean: Target mean intensity after dark subtraction
        tolerance: Acceptable ± range
        exposure_step: Amount to change exposure by if needed (µs)

    Returns:
        True if exposure is acceptable, False otherwise
    """
    if image is None or picam2 is None:
        print("Invalid input to exposure check.")
        return False

    mean_val = image.mean()

    print(f"Mean: {mean_val:.2f}")

    # Check if within acceptable range
    if target_mean - tolerance <= mean_val <= target_mean + tolerance:
        print("Exposure is acceptable.")
        return True

    # Adjust exposure time
    current_exp = picam2.capture_metadata().get("ExposureTime", 5000)
    if mean_val < target_mean:
        new_exp = current_exp + exposure_step
    else:
        new_exp = max(current_exp - exposure_step, 100)

    print(f"Adjusting exposure: {current_exp} → {new_exp}")
    picam2.set_controls({"ExposureTime": int(new_exp)})
    time.sleep(0.5)  # let camera apply new exposure

    return False

def capture_measurement(picam2, measurement_type, fixed_range,
                        light_azimuthal_inc, light_radial_inc,
                        detector_azimuthal_inc, detector_radial_inc,
                        output_folder="Captured_Images"):
    """
    Capture BRDF, BTDF, or both with raw images and motor control.

    Args:
        picam2: initialized camera object.
        measurement_type: "brdf", "btdf", or "both".
        fixed_range: range in degrees.
        *_inc: angle increments in degrees.
    """
    motors = Motors()
    
    if picam2 is None:
        raise ValueError("Camera is not initialized.")

    os.makedirs(output_folder, exist_ok=True)

    # Step counts
    light_az_steps = int(fixed_range / max(light_azimuthal_inc, 1))
    light_rad_steps = int(fixed_range / max(light_radial_inc, 1))
    det_az_steps = int(fixed_range / max(detector_azimuthal_inc, 1))
    det_rad_steps = int(fixed_range / max(detector_radial_inc, 1))
    total_steps = light_az_steps * light_rad_steps * det_az_steps * det_rad_steps
    current_step = 1

    # Base angle settings
    if measurement_type == "brdf":
        light_base = detector_base = 0
    elif measurement_type == "btdf":
        light_base = detector_base = 180
    else:  # both
        light_base = detector_base = 0

    print("Moving all motors to offset position...")
    motors.move_light_to_offset()
    motors.move_detector_to_offset()
    time.sleep(1)

    for az_i in range(light_az_steps):
        light_azimuthal = light_base + az_i * light_azimuthal_inc
        motors.move_light_azimuthal(light_azimuthal)

        for rad_i in range(light_rad_steps):
            light_radial = rad_i * light_radial_inc
            motors.move_light_radial(light_radial)

            for det_az_i in range(det_az_steps):
                det_azimuthal = detector_base + det_az_i * detector_azimuthal_inc

                for det_rad_i in range(det_rad_steps):
                    det_radial = det_rad_i * detector_radial_inc

                    motors.move_detector_azimuthal(det_azimuthal)
                    motors.move_detector_radial(det_radial)
                    time.sleep(0.5)

                    def save_capture(label):
                        filename = f"{label}_Laz{light_azimuthal}_Lrad{light_radial}_Daz{det_azimuthal}_Drad{det_radial}.npy"
                        path = os.path.join(output_folder, filename)
                        raw_array = capture_raw_image(picam2)

                        if raw_array is not None:
                            np.save(path, raw_array)
                            print(f"[{current_step}/{total_steps}] Saved {label.upper()} to {path}")
                        else:
                            print(f"Failed to capture {label.upper()}")

                    if measurement_type in ["brdf", "both"]:
                        save_capture("brdf")

                    if measurement_type in ["btdf", "both"]:
                        save_capture("btdf")

                    current_step += 1

            print("Returning detector to offset...")
            motors.move_detector_to_offset()
            time.sleep(1)

    print(f"Completed full scan: {current_step-1} measurements taken.")
