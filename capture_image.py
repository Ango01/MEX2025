import os

def capture_image(picam2, angle):
  """Capture a RAW10 image at a specific angle and exposure time."""

  if picam2 is None:
    raise ValueError("Camera is not initialized.")
  
  # Create a folder to store images
  output_folder = "Captured_Images"
  os.makedirs(output_folder, exist_ok=True)
  
  # Capture image at given angle
  image_file = os.path.join(output_folder, f"image_{angle}.dng")
  picam2.capture_file(image_file, name="raw")
  print(f"Captured image at {angle} degrees")

  return image_file # Return file path for further processing

