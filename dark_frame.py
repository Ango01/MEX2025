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
    "AnalogueGain": 1.0,   # Set gain to 1.0 (no artificial brightness boost)
    "AeEnable": False,     # Disable auto-exposure
    "AwbEnable": False,    # Disable auto white balance
})

# Create a folder to store images
output_folder = "Captured_Images"
os.makedirs(output_folder, exist_ok=True)

# Start the camera
picam2.start()
time.sleep(1)  # Allow camera to warm up

### ---- Capture the Dark Frame ---- ###
input("Cover the lens and press Enter to capture the dark frame...")
dark_frame_file = os.path.join(output_folder, "dark_frame.dng")
picam2.capture_file(dark_frame_file, name="raw")
print("Dark frame captured.")

# Load the dark frame
with rawpy.imread(dark_frame_file) as raw:
    dark_frame = raw.raw_image_visible.astype(np.float32)  # Convert to float for subtraction

### ---- Capture Scattering Measurements ---- ###
angles = range(0, 10, 10)  # Example: capturing at every 10 degrees

for angle in angles:
    input(f"Press Enter to capture image at {angle} degrees...")

    image_file = os.path.join(output_folder, f"image_{angle}.dng")
    picam2.capture_file(image_file, name="raw")
    print(f"Captured image at {angle} degrees")

    # Open the DNG file using rawpy
    with rawpy.imread(image_file) as raw:
        raw_image = raw.raw_image_visible.astype(np.float32)  # Convert to float for subtraction

    ### ---- Subtract the Dark Frame ---- ###
    corrected_image = np.clip(raw_image - dark_frame, 0, 1023)  # Ensure valid range (0-1023)

    ### ---- Convert RAW10 to RGB ---- ###
    corrected_image_scaled = corrected_image * (65535 / 1023)  # Scale 10-bit to 16-bit
    corrected_image_scaled = np.clip(corrected_image_scaled, 0, 65535).astype(np.uint16)

    rgb_image = cv2.cvtColor(corrected_image_scaled, cv2.COLOR_BayerBG2RGB)

    # Normalize to 8-bit for display
    rgb_display = (rgb_image / 256).astype(np.uint8)

    # Show the corrected RGB image
    plt.figure(figsize=(8, 6))
    plt.imshow(rgb_display)
    plt.title(f"Dark Frame Corrected RGB Image at {angle} Degrees")
    plt.axis("off")
    plt.show()

    # Save the corrected image
    corrected_output_file = os.path.join(output_folder, f"image_{angle}_corrected.png")
    cv2.imwrite(corrected_output_file, cv2.cvtColor(rgb_display, cv2.COLOR_RGB2BGR))
    print(f"Saved corrected image: {corrected_output_file}")

# Stop the camera
picam2.stop()
print("Capture sequence completed.")


