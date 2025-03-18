from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import cv2
import matplotlib.pyplot as plt
import os

# Initialize camera
picam2 = Picamera2()

# Configure RAW10 capture
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
  "ExposureTime": 5000,  # Set exposure time (in microseconds)
  "AnalogueGain": 1.0,    # Set gain to 1.0 (no artificial brightness boost)
  "AeEnable": False,      # Disable auto-exposure
  "AwbEnable": False,     # Disable auto white balance
})

angles = range(0, 10, 10)  # Capture images at every 10 degrees

# Create a folder to store images
output_folder = "Captured_Images"
os.makedirs(output_folder, exist_ok=True)

picam2.start()
time.sleep(1)  # Allow camera to warm up

for angle in angles:
  input(f"Press Enter to capture image at {angle} degrees...")

  image_file = os.path.join(output_folder, f"image_{angle}.dng")
  picam2.capture_file(image_file, name="raw")
  print(f"Captured image at {angle} degrees")

  # Open the DNG file using rawpy
  with rawpy.imread(image_file) as raw:
      raw_image = raw.raw_image_visible.astype(np.uint16)  # Convert to 16-bit

  # Plot histogram of RAW pixel intensities
  plt.figure(figsize=(8, 6))
  plt.hist(raw_image.flatten(), bins=50, color='blue', alpha=0.7, edgecolor='black')
  plt.title(f"Pixel Intensity Histogram at {angle} Degrees")
  plt.xlabel("Pixel Intensity (0-1023)")
  plt.ylabel("Frequency")
  plt.grid(True)
  plt.show()

  # Plot Heatmap of RAW Image
  plt.figure(figsize=(8,6))
  plt.imshow(raw_image, cmap='inferno', aspect='auto')
  plt.colorbar(label="Pixel Intensity (0-1023)")
  plt.title(f"Heatmap of RAW Image at {angle} Degrees")
  plt.xlabel("X Pixels")
  plt.ylabel("Y Pixels")
  plt.show()

  ## ---- Extract Color Channels from SBGGR10 Bayer Pattern ---- ##
  # Bayer pattern: SBGGR (Blue in top-left)
  B = raw_image[0::2, 0::2]     # Blue pixels (every 2nd row, every 2nd column)
  G1 = raw_image[0::2, 1::2]    # Green pixels (row 1, col 2)
  G2 = raw_image[1::2, 0::2]    # Green pixels (row 2, col 1)
  R = raw_image[1::2, 1::2]     # Red pixels (every 2nd row, every 2nd column)

  # Average both Green channels
  G = (G1 + G2) / 2

  # Plot histograms for each color channel
  plt.figure(figsize=(8, 6))
  plt.hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
  plt.hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
  plt.hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
  plt.title(f"Color Channel Histograms at {angle} Degrees")
  plt.xlabel("Pixel Intensity (0-1023)")
  plt.ylabel("Frequency")
  plt.legend()
  plt.grid(True)
  plt.show()

  # Normalize channels (optional, for visualization)
  R_norm = R / np.max(R)
  G_norm = G / np.max(G)
  B_norm = B / np.max(B)

  # Plot Heatmaps of Each Color Channel
  fig, axes = plt.subplots(1, 3, figsize=(18, 6))
  axes[0].imshow(R_norm, cmap='Reds', aspect='auto')
  axes[0].set_title("Red Channel (Scattering Intensity)")
  axes[1].imshow(G_norm, cmap='Greens', aspect='auto')
  axes[1].set_title("Green Channel (Scattering Intensity)")
  axes[2].imshow(B_norm, cmap='Blues', aspect='auto')
  axes[2].set_title("Blue Channel (Scattering Intensity)")
  plt.show()

  # Find Brightest Spot in Each Channel
  _, max_R, _, max_loc_R = cv2.minMaxLoc(R_norm)
  _, max_G, _, max_loc_G = cv2.minMaxLoc(G_norm)
  _, max_B, _, max_loc_B = cv2.minMaxLoc(B_norm)

  print(f"Brightest Spot in Red: {max_loc_R}, Intensity: {max_R:.4f}")
  print(f"Brightest Spot in Green: {max_loc_G}, Intensity: {max_G:.4f}")
  print(f"Brightest Spot in Blue: {max_loc_B}, Intensity: {max_B:.4f}")

picam2.stop()
print("Capture sequence completed.")

