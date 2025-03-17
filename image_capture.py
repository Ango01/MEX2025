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

   # Flatten the image for histogram
   pixel_values = raw_image.flatten()

   # Plot histogram of RAW pixel intensities
   plt.figure(figsize=(8, 6))
   plt.hist(pixel_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
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

   # Print details
   print(f"Min Pixel Value: {np.min(raw_image)}")
   print(f"Max Pixel Value: {np.max(raw_image)}")
   print(f"Mean Intensity: {np.mean(raw_image)}")

   ## ---- Extract Color Channels from SBGGR10 Bayer Pattern ---- ##
   # Bayer pattern: SBGGR (Blue in top-left)
   B = raw_image[0::2, 0::2]     # Blue pixels (every 2nd row, every 2nd column)
   G1 = raw_image[0::2, 1::2]    # Green pixels (row 1, col 2)
   G2 = raw_image[1::2, 0::2]    # Green pixels (row 2, col 1)
   R = raw_image[1::2, 1::2]     # Red pixels (every 2nd row, every 2nd column)

   # Merge both Green channels for better statistics
   G = np.concatenate((G1.flatten(), G2.flatten()))

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

   print(f"Mean Intensity R: {np.mean(R)}")

   # Normalize pixel intensities
   R_norm = R / 1023.0
   G_norm = G / 1023.0
   B_norm = B / 1023.0

   # Store BSDF values
   bsdf_data = {"angle": [], "red_bsdf": [], "green_bsdf": [], "blue_bsdf": []}
   bsdf_data["angle"].append(angle)
   bsdf_data["red_bsdf"].append(R_norm)
   bsdf_data["green_bsdf"].append(G_norm)
   bsdf_data["blue_bsdf"].append(B_norm)

picam2.stop()
print("Capture sequence completed.")

"""""
# Create meshgrid for pixel coordinates
x = np.linspace(0, width // 2 - 1, width // 2)
y = np.linspace(0, height // 2 - 1, height // 2)
X, Y = np.meshgrid(x, y)

# Choose a color channel for fitting (R, G, or B)
Z = R_norm  # Change to G_norm or B_norm if needed

# Flatten data for fitting
x_data = X.ravel()
y_data = Y.ravel()
z_data = Z.ravel()

# Initial parameter guesses: [A, mu_x, mu_y, sigma_x, sigma_y]
p0 = [1.0, width // 4, height // 4, 50, 50]

# Fit the 2D Gaussian to the intensity data
popt, _ = curve_fit(gaussian_2d, (x_data, y_data), z_data, p0=p0)

# Extract fitted parameters
A_fit, mu_x_fit, mu_y_fit, sigma_x_fit, sigma_y_fit = popt
print(f"Fitted 2D Gaussian Parameters:")
print(f"Peak Intensity (A) = {A_fit:.3f}")
print(f"Center (μ_x, μ_y) = ({mu_x_fit:.1f}, {mu_y_fit:.1f})")
print(f"Spread (σ_x, σ_y) = ({sigma_x_fit:.1f}, {sigma_y_fit:.1f})")

# Generate fitted 2D Gaussian for visualization
Z_fit = gaussian_2d((X, Y), *popt).reshape(height // 2, width // 2)

plt.figure(figsize=(8, 6))

# Plot original intensity distribution
plt.subplot(1, 2, 1)
plt.imshow(Z, cmap="hot", extent=[0, width//2, 0, height//2])
plt.colorbar(label="Intensity")
plt.title("Original Intensity Distribution")

# Plot 2D Gaussian Fit
plt.subplot(1, 2, 2)
plt.imshow(Z_fit, cmap="hot", extent=[0, width//2, 0, height//2])
plt.colorbar(label="Fitted Intensity")
plt.title("Fitted 2D Gaussian")

plt.show()
"""
