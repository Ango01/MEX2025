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
  "ExposureTime": 50,     # Set exposure time (in microseconds)
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

  raw_array = picam2.capture_array("raw").view(np.uint16)
  print(f"Captured image at {angle} degrees")

  # Flatten the image for histogram
  pixel_values = raw_array.flatten()

  # Plot histogram of RAW pixel intensities
  plt.figure(figsize=(8, 6))
  plt.hist(pixel_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
  plt.title(f"Pixel Intensity Histogram")
  plt.xlabel("Pixel Intensity (0-1023)")
  plt.ylabel("Frequency")
  plt.grid(True)
  plt.show()

  # Plot Heatmap of RAW Image
  plt.figure(figsize=(8,6))
  plt.imshow(raw_array, cmap='inferno', aspect='auto')
  plt.colorbar(label="Pixel Intensity (0-1023)")
  plt.title(f"Heatmap of RAW Image at {angle} Degrees")
  plt.xlabel("X Pixels")
  plt.ylabel("Y Pixels")
  plt.show()

  ## ---- Extract Color Channels from SBGGR10 Bayer Pattern ---- ##
  # Bayer pattern: SBGGR (Blue in top-left)
  B = raw_array[0::2, 0::2]     # Blue pixels (every 2nd row, every 2nd column)
  G1 = raw_array[0::2, 1::2]    # Green pixels (row 1, col 2)
  G2 = raw_array[1::2, 0::2]    # Green pixels (row 2, col 1)
  R = raw_array[1::2, 1::2]     # Red pixels (every 2nd row, every 2nd column)

  # Merge both Green channels for better statistics
  G = (G1 + G2) / 2

  # Plot histograms for each color channel
  plt.figure(figsize=(8, 6))
  plt.hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
  plt.hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
  plt.hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
  plt.title(f"Color Channel Histograms")
  plt.xlabel("Pixel Intensity (0-1023)")
  plt.ylabel("Frequency")
  plt.legend()
  plt.grid(True)
  plt.show()
  
  # Create side-by-side plot: Grayscale image + histogram
  fig, axs = plt.subplots(1, 2, figsize=(14, 6))

  # Grayscale image
  im = axs[0].imshow(raw_array, cmap='gray', aspect='auto')
  axs[0].set_title(f"Grayscale View")
  axs[0].set_xlabel("X Pixels")
  axs[0].set_ylabel("Y Pixels")
  fig.colorbar(im, ax=axs[0], fraction=0.046, pad=0.04, label="Pixel Intensity")

  # Histogram of grayscale values
  axs[1].hist(raw_array.flatten(), bins=50, color='gray', edgecolor='black', alpha=0.7)
  axs[1].set_title("Grayscale Pixel Intensity Histogram")
  axs[1].set_xlabel("Pixel Intensity (0-1023)")
  axs[1].set_ylabel("Frequency")
  axs[1].grid(True)

  # Save the figure to file
  grayscale_plot_path = os.path.join(output_folder, f"grayscale_plot_{angle}.png")
  plt.tight_layout()
  plt.savefig(grayscale_plot_path)
  plt.show()
  print(f"Saved grayscale + histogram plot at {grayscale_plot_path}")

picam2.stop()
print("Capture sequence completed.")
