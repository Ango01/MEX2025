import os, time, logging, cv2
import numpy as np
from motors import Motors  
from process_image import extract_color_channels, circular_roi_mean, detect_static_noise

def capture_raw_image(picam2):
    """Capture a raw Bayer image and return it as a 16-bit 2D array."""
    try:
        raw_array = picam2.capture_array("raw").view(np.uint16)
        return raw_array

    except Exception as e:
        logging.error(f"Failed to capture RAW image: {e}")
        return None

def check_and_adjust_exposure(picam2, image, target_min=818, target_max=921):
    """
    Adjust exposure so that the mean of the top 5% brightest pixels in the dominant color channel
    falls within 80-90% of the 10-bit range (between 818 and 921).
    """
    if image is None or picam2 is None:
        logging.error("Invalid input to exposure check.")
        return False

    # Extract RGB channels from image
    R, G, B = extract_color_channels(image)

    # Identify dominant channel based on mean intensity
    channel_means = {'R': np.mean(R), 'G': np.mean(G), 'B': np.mean(B)}
    dominant = max(channel_means, key=channel_means.get)
    channel_data = {'R': R, 'G': G, 'B': B}[dominant]

    logging.info(f"Dominant channel: {dominant}")

    # Evaluate top 5% brightest pixels
    flat = channel_data.flatten()
    cutoff = int(len(flat) * 0.05)
    top_pixels = np.sort(flat)[-cutoff:]
    top_mean = np.mean(top_pixels)
    top_median = np.median(top_pixels)
    logging.info(f"Top 5% mean: {top_mean:.2f}, median: {top_median:.2f}")

    # Get current exposure from metadata
    metadata = picam2.capture_metadata()
    current_exp = metadata.get("ExposureTime", 10000)

    # Stop if already within target range
    if target_min <= top_mean <= target_max:
        logging.info("Exposure is acceptable.\n")
        return True
    
    # Calculate difference between top_mean and target midpoint
    target_mid = (target_min + target_max) / 2
    diff_ratio = (top_mean - target_mid) / target_mid  # How far off the image is from target
    scaling_factor = 0.1  # 10% change per unit deviation
    base_step = max(100, int(current_exp * scaling_factor * abs(diff_ratio)))

    # Adjust exposure adaptively
    if top_mean > target_max:
        new_exp = max(current_exp - base_step, 100)
        logging.info(f"Too bright → Decreasing exposure by {base_step} µs")
    else:
        new_exp = current_exp + base_step
        logging.info(f"Too dark → Increasing exposure by {base_step} µs")

    logging.info(f"Adjusting exposure: {current_exp} → {new_exp}")
    picam2.set_controls({"ExposureTime": int(new_exp)})
    time.sleep(1)  # Let settings apply

    return False

def run_full_measurement(app, image_count=10, save_dir="Captured_Data"):
    """Main function to run the full measurement process."""
    picam2 = app.camera
    dark_value = app.dark_value

    # Basic checks
    if picam2 is None or dark_value is None:
        app.set_status("Camera or dark value not set.", "error")
        return

    os.makedirs(save_dir, exist_ok=True)

    # Load angle configurationd from the app
    light_radial_angles = app.light_radial_angles       
    light_azimuth_angles = app.incidence_angles         
    det_azimuth_angles = app.det_azimuth_angles         
    det_radial_angles = app.det_radial_angles           

    motors = Motors()
    # motors.home_detector_axes() # Homing by mechanical stop and then setting offset
    motors.reset_position()

    app.bsdf_measurements = {}  
    app.relative_errors = {}

    capture_index = 1 # Counter for process

    # Scan through all angle combinations
    for light_rad in light_radial_angles:  
        if check_stop(app): return
        motors.move_light_radial(light_rad)

        for light_az in light_azimuth_angles:  
            if check_stop(app): return
            motors.move_light_azimuthal(light_az)

            for det_az in det_azimuth_angles:
                if check_stop(app): return
                motors.move_detector_azimuthal(det_az)

                for det_rad in det_radial_angles:
                    if check_stop(app): return

                    # Skip blocked positions
                    if abs(light_az - det_az) < 2.0 and abs(light_rad - det_rad) < 2.0:
                        logging.warning(f"Skipping blocked configuration at LS({light_az}, {light_rad}) ≈ DET({det_az}, {det_rad})\n")
                        continue
                    
                    motors.move_detector_radial(det_rad)
                    time.sleep(1)

                    # Show current measurement status
                    app.set_status(f"Capturing at LS ({light_rad}, {light_az}) → DET ({det_az}, {det_rad})", "info")

                    corrected_images = []

                    # Exposure adjustment
                    for attempt in range(image_count):
                        if check_stop(app): return
                        test_image = capture_raw_image(picam2)
                        if test_image is None:
                            continue
                        if check_and_adjust_exposure(picam2, test_image):
                            break
                    else:
                        logging.warning("Exposure tuning failed, skipping this position.\n")
                        continue
                    
                    # Capture valid images
                    valid_count = 0 # How many good images are collected
                    attempts = 0
                    max_attempts = image_count * 3 # Limit to prevent infinite loops

                    # Loop continues until desired number of valid images are captured/reached attempt limit
                    while valid_count < image_count and attempts < max_attempts:
                        if check_stop(app): return
                        img = capture_raw_image(picam2)
                        attempts += 1

                        if img is None:
                            logging.error(f"Attempt {attempts}: Image capture failed.")
                            continue

                        if detect_static_noise(img):
                            logging.info(f"Attempt {attempts}: Image rejected due to static noise.\n")
                            continue
                        
                        # Subtract dark value and clip negatives
                        corrected = np.clip(img.astype(np.float32) - dark_value, 0, None)
                        corrected_images.append(corrected)
                        valid_count += 1

                        # Save corrected image as JPG
                        filename =  f"LS({light_rad}_{light_az})_DET({det_az}_{det_rad}).jpg"
                        save_path = os.path.join(save_dir, filename)

                        # Normalize to 8-bit for visualization
                        normalized = cv2.normalize(corrected, None, 0, 255, cv2.NORM_MINMAX)
                        normalized = normalized.astype(np.uint8)

                        # Convert to 3-channel grayscale for consistent JPG
                        three_channel = cv2.merge([normalized]*3)

                        cv2.imwrite(save_path, three_channel)
                    
                    if len(corrected_images) < image_count:
                        logging.warning(f"Warning: Only {len(corrected_images)} valid images collected (out of {image_count} required)\n")

                    # Process and store result 
                    if corrected_images:
                        combined = np.mean(corrected_images, axis=0)
                        R, G, B = extract_color_channels(combined)

                        r_mean, r_err = circular_roi_mean(R)
                        g_mean, g_err = circular_roi_mean(G)
                        b_mean, b_err = circular_roi_mean(B)

                        # Store error estimates
                        app.relative_errors[(light_az, light_rad, det_az, det_rad)] = (r_err, g_err, b_err)
                        logging.info(f"Rel. Errors - R: {r_err:.4f}, G: {g_err:.4f}, B: {b_err:.4f}")

                        # Store final mean values for BSDF
                        logging.info(f"ROI Mean Intensities - R: {r_mean:.2f}, G: {g_mean:.2f}, B: {b_mean:.2f}")
                        key = (light_rad, light_az, det_az, det_rad)
                        app.bsdf_measurements[key] = (r_mean, g_mean, b_mean)

                    capture_index += 1

            motors.move_detector_to_offset()
            time.sleep(1)

    motors.move_light_to_offset()
    app.set_status("Full measurement complete.", "success")
    logging.info("Full measurement complete.\n")

def check_stop(app):
    """Return True if the user has requested the measurement to stop."""
    return getattr(app, "stop_requested", False)