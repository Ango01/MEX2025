from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import cv2
import matplotlib.pyplot as plt

# Initialize camera
picam2 = Picamera2()

# Configure RAW capture
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
   "ExposureTime": 1000,  # Set exposure time (in microseconds)
   "AnalogueGain": 1.0,    # Set gain to 1.0 (no artificial brightness boost)
   "AeEnable": False,      # Disable auto-exposure
   "AwbEnable": False,     # Disable auto white balance
})

# Start camera and capture RAW data
picam2.start()
time.sleep(1)

dng_file = "image.dng"
picam2.capture_file(dng_file, name="raw")

picam2.stop()

# Open the DNG file using rawpy
with rawpy.imread(dng_file) as raw:
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
print("Min intensity:", np.min(pixel_values))
print("Max intensity:", np.max(pixel_values))
print("Mean intensity:", np.mean(pixel_values))

# Plot histogram of pixel intensity values
plt.figure(figsize=(8, 6))
plt.hist(pixel_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
plt.title("Pixel Intensity Histogram (RAW10 Data)")
plt.xlabel("Pixel Intensity (0-1023)")
plt.ylabel("Frequency")
plt.grid(True)
plt.show()

print("Histogram plotted successfully. Grayscale image saved as 'converted_image.png'.")

#Get image dimensions
height, width = raw_image.shape

# Extract color channels from Bayer pattern (SRGGB)
B = raw_image[0::2, 0::2]  # Red pixels (every other row and column)
G1 = raw_image[0::2, 1::2]  # Green pixels (top-left)
G2 = raw_image[1::2, 0::2]  # Green pixels (bottom-right)
R = raw_image[1::2, 1::2]  # Blue pixels (every other row and column)

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

