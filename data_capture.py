from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import cv2
import matplotlib.pyplot as plt

# Initialize camera
picam2 = Picamera2()

# Configure RAW10 capture
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
  "ExposureTime": 1000,  # Set exposure time (in microseconds)
  "AnalogueGain": 1.0,    # Set gain to 1.0 (no artificial brightness boost)
  "AeEnable": False,      # Disable auto-exposure
  "AwbEnable": False,     # Disable auto white balance
})

# Start camera and capture RAW data in a file
picam2.start()
time.sleep(1)

image_file = "image.dng"
picam2.capture_file(image_file, name="raw")

picam2.stop()

# Open the DNG file using rawpy
with rawpy.imread(image_file) as raw:
   # Extract the raw sensor data
   raw_image = raw.raw_image_visible.astype(np.uint16)  # Convert to 16-bit

# Normalize the intensity values to range 0-1023 (10-bit)
max_value = 1023  # Since RAW10 stores 10-bit pixel values
normalized_image = (raw_image / max_value) * 255  # Scale to 8-bit (0-255)
normalized_image = normalized_image.astype(np.uint8)

# Save the extracted grayscale image for verification
cv2.imwrite("converted_image.png", normalized_image)

# Flatten the image array to 1D for histogram plotting
pixel_values = raw_image.flatten()

# Plot histogram of pixel intensity values
plt.figure(figsize=(8, 6))
plt.hist(pixel_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
plt.title("Pixel Intensity Histogram (RAW10 Data)")
plt.xlabel("Pixel Intensity (0-1023)")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()

print("Histogram plotted successfully. Grayscale image saved as 'converted_image.png'.")

# Get image dimensions
height, width = raw_image.shape

# Extract color channels from Bayer pattern (SBGGR)
B = raw_image[0::2, 0::2]   # Blue pixels (even rows, even cols)
G1 = raw_image[0::2, 1::2]  # Green pixels (even rows, odd cols)
G2 = raw_image[1::2, 0::2]  # Green pixels (odd rows, even cols)
R = raw_image[1::2, 1::2]   # Red pixels (odd rows, odd cols)

# Merge both green channels (optional, or analyze separately)
G = (G1 + G2) / 2

# Flatten pixel values for histogram plotting
R_flat = R.flatten()
G_flat = G.flatten()
B_flat = B.flatten()

# Plot histogram for all channels on the same plot
plt.figure(figsize=(8, 6))
plt.hist(R_flat, bins=50, color='red', alpha=0.6, edgecolor='black', label="Red Channel")
plt.hist(G_flat, bins=50, color='green', alpha=0.6, edgecolor='black', label="Green Channel")
plt.hist(B_flat, bins=50, color='blue', alpha=0.6, edgecolor='black', label="Blue Channel")

plt.title("Pixel Intensity Histogram (RAW10 Data)")
plt.xlabel("Pixel Intensity (0-1023)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()

print("Histogram plotted successfully for all color channels.")

"""""
R_norm = R / 1023.0
G_norm = G / 1023.0
B_norm = B / 1023.0

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

# Resize extracted channels to match original image size
R_resized = cv2.resize(R, (width, height), interpolation=cv2.INTER_LINEAR)
G_resized = cv2.resize(G, (width, height), interpolation=cv2.INTER_LINEAR)
B_resized = cv2.resize(B, (width, height), interpolation=cv2.INTER_LINEAR)


# Save or display the image
plt.imshow(G_resized)

plt.title("Reconstructed RGB Image")
plt.show()
"""
