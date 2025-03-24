import os
import json
import process_image

def capture_image(picam2, meas_type, light_angle, detector_angle, output_folder):
    """Capture a RAW10 image using an initialized Picamera2 instance."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    filename = f"{meas_type}_L{light_angle:.1f}_D{detector_angle:.1f}.dng"
    image_file = os.path.join(output_folder, filename)

    picam2.capture_file(image_file, name="raw")
    print(f"Captured image: {image_file}")
    save_metadata(image_file, meas_type, light_angle, detector_angle)

    return image_file

def capture_measurement(picam2, measurement_type,
                        light_num_steps, light_azimuthal_inc, light_radial_inc,
                        detector_num_steps, detector_azimuthal_inc, detector_radial_inc):
    """Capture BRDF, BTDF, or both with metadata and processing."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    output_folder = "Captured_Images"
    os.makedirs(output_folder, exist_ok=True)

    total_steps = light_num_steps * detector_num_steps
    current_step = 1

    for i in range(light_num_steps):
        current_light_azimuthal = i * light_azimuthal_inc
        current_light_radial = i * light_radial_inc

        print(f"[Light] Position {i+1}/{light_num_steps} at Azimuthal {current_light_azimuthal}°, Radial {current_light_radial}°")

        for j in range(detector_num_steps):
            current_detector_azimuthal = j * detector_azimuthal_inc
            current_detector_radial = j * detector_radial_inc

            print(f"[Detector] Position {j+1}/{detector_num_steps} at Azimuthal {current_detector_azimuthal}°, Radial {current_detector_radial}°")

            if measurement_type in ["brdf", "both"]:
                print(f"[{current_step}/{total_steps}] Capturing BRDF...")
                image_file = capture_image(picam2, "brdf", current_light_azimuthal, current_detector_azimuthal, output_folder)
                if image_file:
                    process_single_image(image_file, "brdf", current_light_azimuthal, current_detector_azimuthal)

            if measurement_type in ["btdf", "both"]:
                print(f"[{current_step}/{total_steps}] Capturing BTDF...")
                image_file = capture_image(picam2, "btdf", current_light_azimuthal, current_detector_azimuthal, output_folder)
                if image_file:
                    process_single_image(image_file, "btdf", current_light_azimuthal, current_detector_azimuthal)

            current_step += 1

    print(f"Completed full scan with {light_num_steps} light positions and {detector_num_steps} detector positions each.")

def process_single_image(image_file, meas_type, light_angle, detector_angle):
    raw_image = process_image.process_raw_image(image_file)
    R, G, B = process_image.extract_color_channels(raw_image)
    process_image.calculate_scattering(R, G, B, meas_type, light_angle, detector_angle)

def save_metadata(image_file, meas_type, light_angle, detector_angle):
    metadata_file = image_file.replace(".dng", ".json")
    metadata = {
        "measurement_type": meas_type,
        "light_azimuthal": light_angle,
        "detector_azimuthal": detector_angle
    }
    
    with open(metadata_file, "w") as f:
        json.dump(metadata, f, indent=4)