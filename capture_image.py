import os

def capture_image(picam2):
  """Capture a RAW10 image at a specific angle."""

  if picam2 is None:
    raise ValueError("Camera is not initialized.")
    
  output_folder = "Captured_Images"
  os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

  image_count = len(os.listdir(output_folder))  # Count existing images for unique filenames
  image_file = os.path.join(output_folder, f"image_{image_count}.dng")

  try:
    picam2.capture_file(image_file, name="raw")
    print(f"Captured image: {image_file}")
  except Exception as e:
    print(f"Error capturing image: {e}")
    return None  # Return None on failure

  return image_file