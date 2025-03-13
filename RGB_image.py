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
config = picam2.create_still_configuration(raw={"format": "SBGGR10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
   "ExposureTime": 1000,  # Set exposure time (in microseconds)
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

   ## ---- Convert RAW10 Bayer to RGB using OpenCV ---- ##
   # Normalize to full 16-bit (scale up from 10-bit)
   raw_image_scaled = raw_image * (65535 // 1023)  # Scale 10-bit values to 16-bit range
   raw_image_scaled = np.clip(raw_image_scaled, 0, 65535).astype(np.uint16)  # Ensure valid range

   # Convert using OpenCV demosaicing (SBGGR10 → RGB)
   rgb_image = cv2.cvtColor(raw_image_scaled, cv2.COLOR_BayerBG2RGB)

   # Normalize for display (convert 16-bit to 8-bit)
   rgb_display = (rgb_image / 256).astype(np.uint8)  # Scale from 16-bit (0-65535) to 8-bit (0-255)

   # Show RGB image
   plt.figure(figsize=(8, 6))
   plt.imshow(rgb_display)
   plt.title(f"RGB Image at {angle} Degrees")
   plt.axis("off")
   plt.show()

   # Save RGB image
   rgb_output_file = os.path.join(output_folder, f"image_{angle}_RGB.png")
   cv2.imwrite(rgb_output_file, cv2.cvtColor(rgb_display, cv2.COLOR_RGB2BGR))  # Convert RGB to BGR for OpenCV saving
   print(f"Saved RGB image: {rgb_output_file}")

picam2.stop()
print("Capture sequence completed.")



