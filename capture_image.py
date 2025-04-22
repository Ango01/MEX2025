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

def capture_measurement(picam2, measurement_type, fixed_range,
                        light_azimuthal_inc, light_radial_inc,
                        detector_azimuthal_inc, detector_radial_inc):
    """Capture BRDF, BTDF, or both with metadata and motor control."""
    motors = Motors()
    
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    output_folder = "Captured_Images"
    os.makedirs(output_folder, exist_ok=True)

    # Calculate steps
    light_az_steps = int(fixed_range / max(light_azimuthal_inc, 1))
    light_rad_steps = int(fixed_range / max(light_radial_inc, 1))
    det_az_steps = int(fixed_range / max(detector_azimuthal_inc, 1))
    det_rad_steps = int(fixed_range / max(detector_radial_inc, 1))
    total_steps = light_az_steps * light_rad_steps * det_az_steps * det_rad_steps
    current_step = 1

    # Measurement base direction
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
        print(f"[Light] Azimuthal Step {az_i+1}/{light_az_steps} at {light_azimuthal}°")

        for rad_i in range(light_rad_steps):
            light_radial = rad_i * light_radial_inc
            motors.move_light_radial(light_radial)
            print(f"[Light] Radial Step {rad_i+1}/{light_rad_steps} at {light_radial}°")

            for det_az_i in range(det_az_steps):
                det_azimuthal = detector_base + det_az_i * detector_azimuthal_inc

                for det_rad_i in range(det_rad_steps):
                    det_radial = det_rad_i * detector_radial_inc

                    print(f"[Detector] Az {det_azimuthal}°, Rad {det_radial}°")

                    motors.move_detector_azimuthal(det_azimuthal)
                    motors.move_detector_radial(det_radial)
                    time.sleep(0.5)

                    if measurement_type in ["brdf", "both"]:
                        print(f"[{current_step}/{total_steps}] Capturing BRDF...")
                        image_file = capture_image(picam2, "brdf", light_azimuthal, det_azimuthal, output_folder)
                        if image_file:
                            process_single_image(image_file)

                    if measurement_type in ["btdf", "both"]:
                        print(f"[{current_step}/{total_steps}] Capturing BTDF...")
                        image_file = capture_image(picam2, "btdf", light_azimuthal, det_azimuthal, output_folder)
                        if image_file:
                            process_single_image(image_file)

                    current_step += 1

            # Return detector to offset before light moves again
            print("Returning detector to offset...")
            motors.move_detector_to_offset()
            time.sleep(1)

    print(f"Completed full scan: {current_step-1} measurements taken.")


def process_single_image(image_file):
    raw_image = process_image.process_raw_image(image_file)
    R, G, B = process_image.extract_color_channels(raw_image)
    # ROI
    # Mean Intensity