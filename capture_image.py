import os
import process_image

def capture_measurement(picam2, measurement_type, num_steps, angle_light_azimuthal, angle_light_radial, angle_detector_azimuthal, angle_detector_radial):
  """Capture BRDF, BTDF, or both based on user selection."""
  if picam2 is None:
    raise ValueError("Camera is not initialized. Call initialize_camera() first.")

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
      process_image.save_intensity_data(image_file, current_angle_light_azimuthal, measurement_type="BRDF")

    # Measure BTDF (Transmission)
    if measurement_type in ["btdf", "both"]:
      print(f"Capturing BTDF at {current_angle_detector_azimuthal}°, {current_angle_detector_radial}°")
      image_file = capture_image(picam2)
      process_image.save_intensity_data(image_file, current_angle_detector_azimuthal, measurement_type="BTDF")

    print(f"Completed step {i+1}/{num_steps}")


def capture_image(picam2, output_folder="Captured_Images"):
    """Capture a RAW10 image using an initialized Picamera2 instance."""
    if picam2 is None:
        raise ValueError("Camera is not initialized. Call initialize_camera() first.")
    
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
