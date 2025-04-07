import os
import json
import time
import motors  # Arduino motor control functions
import process_image

def capture_image(picam2, meas_type, light_angle, detector_angle, output_folder):
    """Capture a RAW10 image using an initialized Picamera2 instance."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    filename = f"{meas_type}_L{light_angle:.1f}_D{detector_angle:.1f}.dng"
    image_file = os.path.join(output_folder, filename)

    picam2.capture_file(image_file, name="raw")
    print(f"Captured image: {image_file}")

    return image_file

def capture_measurement(picam2, measurement_type, fixed_range,
                        light_azimuthal_inc, light_radial_inc,
                        detector_azimuthal_inc, detector_radial_inc):
    """Capture BRDF, BTDF, or both with metadata and motor control."""

    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")

    output_folder = "Captured_Images"
    os.makedirs(output_folder, exist_ok=True)

    # Calculate steps from increments
    light_steps = int(fixed_range / max(light_azimuthal_inc, 1))
    detector_steps = int(fixed_range / max(detector_azimuthal_inc, 1))
    total_steps = light_steps * detector_steps
    current_step = 1

    # Set angular offset depending on measurement type
    if measurement_type == "brdf":
        light_base = detector_base = 0
    elif measurement_type == "btdf":
        light_base = detector_base = 180
    else:  # "both"
        light_base = detector_base = 0

    for i in range(light_steps):
        light_azimuthal = light_base + i * light_azimuthal_inc
        light_radial = i * light_radial_inc

        print(f"[Light] Position {i+1}/{light_steps} at Azimuthal {light_azimuthal}°, Radial {light_radial}°")

        # Move light source
       # motors.move_light_azimuthal(light_azimuthal)
        #motors.move_light_radial(light_radial)
        #time.sleep(0.5)

        for j in range(detector_steps):
            detector_azimuthal = detector_base + j * detector_azimuthal_inc
            detector_radial = j * detector_radial_inc

            print(f"[Detector] Position {j+1}/{detector_steps} at Azimuthal {detector_azimuthal}°, Radial {detector_radial}°")

            # Move detector
            motors.move_detector_azimuthal(detector_azimuthal)
            motors.move_detector_radial(detector_radial)
            time.sleep(0.5)

            # Capture image depending on measurement type
            if measurement_type in ["brdf", "both"]:
                print(f"[{current_step}/{total_steps}] Capturing BRDF...")
                image_file = capture_image(picam2, "brdf", light_azimuthal, detector_azimuthal, output_folder)
                if image_file:
                    process_single_image(image_file, "brdf", light_azimuthal, detector_azimuthal)

            if measurement_type in ["btdf", "both"]:
                print(f"[{current_step}/{total_steps}] Capturing BTDF...")
                image_file = capture_image(picam2, "btdf", light_azimuthal, detector_azimuthal, output_folder)
                if image_file:
                    process_single_image(image_file, "btdf", light_azimuthal, detector_azimuthal)

            current_step += 1

    print(f"Completed full scan with {light_steps} light positions and {detector_steps} detector positions.")

def process_single_image(image_file):
    raw_image = process_image.process_raw_image(image_file)
    R, G, B = process_image.extract_color_channels(raw_image)
    # ROI
    # Mean Intensity