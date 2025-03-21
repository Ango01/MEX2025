import os
import process_image

def capture_measurement(picam2, measurement_type,
                        light_num_steps, light_azimuthal_inc, light_radial_inc,
                        detector_num_steps, detector_azimuthal_inc, detector_radial_inc):
    """Capture BRDF, BTDF, or both using nested loop logic for light and detector."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    captured_images = []

    for i in range(light_num_steps):
        current_light_azimuthal = i * light_azimuthal_inc
        current_light_radial = i * light_radial_inc

        # In real setup, move light source motors here
        print(f"[Light] Position {i+1}/{light_num_steps} at Azimuthal {current_light_azimuthal}°, Radial {current_light_radial}°")

        for j in range(detector_num_steps):
            current_detector_azimuthal = j * detector_azimuthal_inc
            current_detector_radial = j * detector_radial_inc

            # In real setup, move detector motors here
            print(f"[Detector] Position {j+1}/{detector_num_steps} at Azimuthal {current_detector_azimuthal}°, Radial {current_detector_radial}°")

            # Capture based on measurement type
            if measurement_type in ["brdf", "both"]:
                print("Capturing BRDF image...")
                image_file = capture_image(picam2)
                if image_file:
                    captured_images.append((image_file, "brdf", current_light_azimuthal, current_detector_azimuthal))

            if measurement_type in ["btdf", "both"]:
                print("Capturing BTDF image...")
                image_file = capture_image(picam2)
                if image_file:
                    captured_images.append((image_file, "btdf", current_light_azimuthal, current_detector_azimuthal))

    print(f"Completed full scan with {light_num_steps} light positions and {detector_num_steps} detector positions each.")

    # Process each image after capture
    for image_file, meas_type, light_angle, detector_angle in captured_images:
        raw_image = process_image.process_raw_image(image_file)
        R, G, B = process_image.extract_color_channels(raw_image)
        # Optional: Call user-defined scattering calculations here
        # process_image.calculate_scattering(R, G, B, meas_type, light_angle, detector_angle)

def capture_image(picam2):
    """Capture a RAW10 image using an initialized Picamera2 instance."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    output_folder = "Captured_Images"
    os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

    image_count = len(os.listdir(output_folder))  # Count existing images for unique filenames
    image_file = os.path.join(output_folder, f"image_{image_count}.dng")

    try:
        picam2.capture_file(image_file, name="raw")  # Capture the image
        print(f"Captured image: {image_file}")
    except Exception as e:
        print(f"Error capturing image: {e}")
        return None

    return image_file  # Return the saved image path