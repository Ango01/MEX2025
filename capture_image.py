import os
import process_image

def capture_measurement(picam2, measurement_type, num_steps, angle_light_azimuthal, angle_light_radial, angle_detector_azimuthal, angle_detector_radial):
  """Capture BRDF, BTDF, or both based on user selection."""
  if picam2 is None:
    raise ValueError("Camera is not initialized. Call initialize_camera() first.")

  captured_images = []

  for i in range(num_steps):
    # Compute angles for this step
    current_angle_light_azimuthal = i * angle_light_azimuthal
    current_angle_light_radial = i * angle_light_radial
    current_angle_detector_azimuthal = i * angle_detector_azimuthal
    current_angle_detector_radial = i * angle_detector_radial

    # Measure BRDF (Reflection)
    if measurement_type in ["brdf", "both"]:
      print(f"Capturing BRDF at {current_angle_light_azimuthal}°, {current_angle_light_radial}°")
      image_file = capture_image(picam2)
      if image_file:
        captured_images.append((image_file, "brdf", current_angle_light_azimuthal))

    # Measure BTDF (Transmission)
    if measurement_type in ["btdf", "both"]:
      print(f"Capturing BTDF at {current_angle_detector_azimuthal}°, {current_angle_detector_radial}°")
      image_file = capture_image(picam2)
      if image_file:
        captured_images.append((image_file, "btdf", current_angle_detector_azimuthal))

    print(f"Completed step {i+1}/{num_steps}")

  # Process each image after capture
  for image_file, meas_type, angle in captured_images:
    raw_image = process_image.process_raw_image(image_file)
    R, G, B = process_image.extract_color_channels(raw_image)
    # Call user-defined scattering calculations here
    #process_image.calculate_scattering(R, G, B, meas_type, angle)

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
