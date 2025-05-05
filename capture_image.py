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

def check_and_adjust_exposure(picam2, image, target_min=818, target_max=921, exposure_step=100):
    """
    Adjusts exposure to ensure the mean of the top 5% brightest pixels in the dominant color channel
    falls within 80-90% of the 10-bit range (i.e., between 818 and 921).
    """
    if image is None or picam2 is None:
        print("Invalid input to exposure check.")
        return False

    # Extract color channels
    R, G, B = extract_color_channels(image)

    # Determine the dominant channel by max mean intensity
    channel_means = {
        'R': np.mean(R),
        'G': np.mean(G),
        'B': np.mean(B)
    }
    dominant = max(channel_means, key=channel_means.get)
    channel_data = {'R': R, 'G': G, 'B': B}[dominant]

    print(f"Dominant channel: {dominant}")

    # Flatten the channel and get top 5% pixel values
    flat = channel_data.flatten()
    cutoff = int(len(flat) * 0.05)
    top_pixels = np.sort(flat)[-cutoff:]
    top_mean = np.mean(top_pixels)

    print(f"Mean of top 5% pixels in {dominant}: {top_mean:.2f}")

    # Get current exposure
    metadata = picam2.capture_metadata()
    current_exp = metadata.get("ExposureTime", 10000)

    if target_min <= top_mean <= target_max:
        print("Exposure is acceptable.")
        return True

    # Adjust exposure
    if top_mean > target_max:
        new_exp = max(current_exp - exposure_step, 100)
        print("Too bright → Decreasing exposure")
    else:
        new_exp = current_exp + exposure_step
        print("Too dark → Increasing exposure")

    print(f"Adjusting exposure: {current_exp} → {new_exp}")
    picam2.set_controls({"ExposureTime": int(new_exp)})
    time.sleep(1)  # Let settings apply

    return False

def run_full_measurement(app, image_count=10, save_dir="Captured_Data"):
    """Main function to run the full measurement process."""
    picam2 = app.camera
    dark_value = app.dark_value

    if picam2 is None or dark_value is None:
        app.set_status("Camera or dark value not set.", "error")
        return

    os.makedirs(save_dir, exist_ok=True)

    # Retrieve angles from app (Step 4)
    light_radial_angles = app.light_radial_angles       # SampleRotation
    light_azimuth_angles = app.incidence_angles         # AngleOfIncidence
    det_azimuth_angles = app.det_azimuth_angles         # ScatterAzimuth
    det_radial_angles = app.det_radial_angles           # ScatterRadial

    motors = Motors()
    app.bsdf_measurements = {}  # Reset previous data
    app.relative_errors = {}

    capture_index = 1

    for light_rad in light_radial_angles:  # Sample rotation
        if check_stop(app): return
        motors.move_light_radial(light_rad)

        for light_az in light_azimuth_angles:  # Incidence
            if check_stop(app): return
            motors.move_light_azimuthal(light_az)

            for det_az in det_azimuth_angles:
                if check_stop(app): return
                motors.move_detector_azimuthal(det_az)

                for det_rad in det_radial_angles:
                    if check_stop(app): return
                    motors.move_detector_radial(det_rad)
                    time.sleep(1)

                    app.set_status(
                        f"Capturing at LS ({light_rad}, {light_az}) → DET ({det_az}, {det_rad})", "info"
                    )

                    corrected_images = []

                    # Auto exposure loop
                    for attempt in range(image_count):
                        if check_stop(app): return
                        test_image = capture_raw_image(picam2)
                        if test_image is None:
                            continue
                        if check_and_adjust_exposure(picam2, test_image):
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
                        corrected_images.append(corrected)

                    if corrected_images:
                        combined = np.mean(corrected_images, axis=0)
                        R, G, B = extract_color_channels(combined)

                        r_mean, r_err = circular_roi_mean(R)
                        g_mean, g_err = circular_roi_mean(G)
                        b_mean, b_err = circular_roi_mean(B)

                        app.relative_errors[(light_az, light_rad, det_az, det_rad)] = (r_err, g_err, b_err)
                        print(f"Rel. Errors - R: {r_err:.4f}, G: {g_err:.4f}, B: {b_err:.4f}")

                        print(f"ROI Mean Intensities - R: {r_mean:.2f}, G: {g_mean:.2f}, B: {b_mean:.2f}")

                        # Use correct 4-angle key
                        key = (light_rad, light_az, det_az, det_rad)
                        app.bsdf_measurements[key] = (r_mean, g_mean, b_mean)

                    capture_index += 1

            motors.move_detector_to_offset()
            time.sleep(1)

    motors.move_light_to_offset()
    app.set_status("Full measurement complete.", "success")
    print("Full measurement complete.")

def check_stop(app):
    """Check if a stop request has been triggered (for interrupting measurement)."""
    if getattr(app, "stop_requested", False):
        return True
    return False