import os
import time
import numpy as np
from motors import Motors  
from process_image import extract_color_channels, circular_roi_mean
from Steps.step4_angle_steps import RANGE_MAP

def capture_raw_image(picam2):
    """Capture a raw Bayer image and return it as a 16-bit 2D array."""
    try:
        raw_array = picam2.capture_array("raw").view(np.uint16)
        return raw_array

    except Exception as e:
        print(f"Failed to capture RAW image: {e}")
        return None

def check_and_adjust_exposure(picam2, image, target_max=972, tolerance=10, exposure_step=50):
    """
    Adjust exposure to keep the brightest color channel within a target range.
    Uses max value from the most intense channel (R, G, or B). 
    """
    if image is None or picam2 is None:
        print("Invalid input to exposure check.")
        return False

    # Separate image into R, G, B channels
    R, G, B = extract_color_channels(image)

    # Find maximum value in each color channel
    max_values = {'R': R.max(), 'G': G.max(), 'B': B.max()}
    priority_channel = max(max_values, key=max_values.get) # Channel with highest max
    priority_value = max_values[priority_channel]

    print(f"Max R: {max_values['R']}, Max G: {max_values['G']}, Max B: {max_values['B']}")
    print(f"Prioritizing channel: {priority_channel} (value: {priority_value})")

    # Get current exposure time from metadata
    metadata = picam2.capture_metadata()
    current_exp = metadata.get("ExposureTime", 10000) # Fallback to 10000 µs

    # Check if max value within acceptable range
    if target_max - tolerance <= priority_value <= target_max + tolerance:
        print("Exposure is acceptable.")
        return True

    # Adjust exposure time up or down based on brightness
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

def run_full_measurement(app, image_count=10, save_dir="Captured_Data"):
    """Main function to run the full measurement process."""
    picam2 = app.camera
    dark_value = app.dark_value

    if picam2 is None or dark_value is None:
        app.set_status("Camera or dark value not set.", "error")
        return

    os.makedirs(save_dir, exist_ok=True)

    # Get angular range based on measurement type
    mtype = app.measurement_type.get() if hasattr(app, "measurement_type") else "BRDF"
    start_angle, end_angle = RANGE_MAP.get(mtype, (8, 175))

    step_counts = app.step_counts
    step_sizes = app.angle_step_sizes

    # Get angle step sizes from combobox values
    ls_az_step = step_sizes["ls_az"]
    ls_rad_step = step_sizes["ls_rad"]
    det_az_step = step_sizes["det_az"]
    det_rad_step = step_sizes["det_rad"]

    # Get number of steps from stored counts
    ls_az_steps = step_counts["ls_az"]
    ls_rad_steps = step_counts["ls_rad"]
    det_az_steps = step_counts["det_az"]
    det_rad_steps = step_counts["det_rad"]

    # Initialize motors
    motors = Motors()
    motors.move_light_to_offset()
    motors.move_detector_to_offset()

    capture_index = 1

    for laz_i in range(ls_az_steps):
        if check_stop(app): return
        light_az = start_angle + laz_i * ls_az_step
        motors.move_light_azimuthal(light_az)

        for lrad_i in range(ls_rad_steps):
            if check_stop(app): return
            #light_rad = start_angle + lrad_i * ls_rad_step
            light_rad = app.incidence_angles[lrad_i]
            motors.move_light_radial(light_rad)

            for daz_i in range(det_az_steps):
                if check_stop(app): return
                #det_az = start_angle + daz_i * det_az_step
                det_az = app.azimuth_angles[daz_i]
                motors.move_detector_azimuthal(det_az)

                for drad_i in range(det_rad_steps):
                    if check_stop(app): return
                    #det_rad = start_angle + drad_i * det_rad_step
                    det_rad = app.radial_angles[drad_i]
                    motors.move_detector_radial(det_rad)
                    time.sleep(1)

                    corrected_images = []

                    # Try up to 10 times to adjust exposure
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
                    
                    # Capture and save images
                    for rep in range(image_count):
                        if check_stop(app): return
                        img = capture_raw_image(picam2)
                        if img is None:
                            print(f"Image {rep+1} failed.")
                            continue
                        
                        corrected = np.clip(img.astype(np.float32) - dark_value, 0, None) # Subtract dark value
                        corrected_images.append(corrected)

                        exposure = picam2.capture_metadata().get("ExposureTime", None)

                        print(f"Final Exposure Time: ", exposure)

                    if corrected_images:
                        combined = np.mean(corrected_images, axis=0)

                        # Extract channels
                        R, G, B = extract_color_channels(combined)

                        # Get ROI means
                        r_mean = circular_roi_mean(R)
                        g_mean = circular_roi_mean(G)
                        b_mean = circular_roi_mean(B)
                    
                        print(f"ROI Mean Intensities - R: {r_mean:.2f}, G: {g_mean:.2f}, B: {b_mean:.2f}")

                        if not hasattr(app, "bsdf_measurements"):
                            app.bsdf_measurements = {}

                        # Key: (light incidence angle, detector azimuth angle)
                        key = (light_rad, det_az)

                        # Initialize 2D grid [azimuth index][radial index] if first time
                        if key not in app.bsdf_measurements:
                            app.bsdf_measurements[key] = [
                                [None for _ in range(det_rad_steps)] for _ in range(det_az_steps)
                            ]

                        # Store the [R,G,B] mean intensity at the correct azimuth/radial position
                        app.bsdf_measurements[key][daz_i][drad_i] = (r_mean, g_mean, b_mean)

                    capture_index += 1

            # Reset detector
            motors.move_detector_to_offset()
            time.sleep(1)

    motors.move_light_to_offset()
    print("Full measurement complete.")

def check_stop(app):
    """Check if a stop request has been triggered (for interrupting measurement)."""
    if getattr(app, "stop_requested", False):
        return True
    return False