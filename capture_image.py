import os

def capture_image(picam2, angle):
  """Capture a RAW10 image at a specific angle."""

  if picam2 is None:
    raise ValueError("Camera is not initialized.")
    
  output_folder = "Captured_Images"
  os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

  image_file = os.path.join(output_folder, f"image_{angle}.dng")

  try:
    picam2.capture_file(image_file, name="raw")
    print(f"Captured image at {angle} degrees")
  except Exception as e:
    print(f"Error capturing image at {angle} degrees: {e}")
    return None  # Return None on failure

  return image_file