
from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import cv2
import matplotlib.pyplot as plt
import os
import pandas as pd

# Initialize camera
picam2 = Picamera2()

# Configure RAW10 capture
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
    "ExposureTime": 5000,   # Set exposure time (in microseconds)
    "AnalogueGain": 1.0,    # Set gain to 1.0 (no artificial brightness boost)
    "AeEnable": False,      # Disable auto-exposure
    "AwbEnable": False,     # Disable auto white balance
})

angles = range(0, 10, 10)  # Capture images at every 10 degrees

# Create folders
output_folder = "Captured_Images"
processed_folder = "Processed_Data"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(processed_folder, exist_ok=True)

# Start camera
picam2.start()
time.sleep(1)  # Allow camera to warm up

# Store BSDF data
bsdf_data = []

for angle in angles:
    input(f"Press Enter to capture image at {angle} degrees...")

    # Capture and save RAW10 image
    image_file = os.path.join(output_folder, f"image_{angle}.dng")
    picam2.capture_file(image_file, name="raw")
    print(f"Captured image at {angle} degrees")
 
    # Read the RAW image and apply demosaicing
    with rawpy.imread(image_file) as raw:
        demosaiced_image = raw.postprocess(
            use_camera_wb=False,  # Disable white balance
            no_auto_bright=True,  # No automatic brightness adjustment
            gamma=(1, 1),         # Linear gamma (no artificial correction)        
            output_bps=16,        # Keep 16-bit depth
            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD  # High-quality demosaicing
        )

    # Save the demosaiced image
    demosaic_file = os.path.join(output_folder, f"demosaiced_{angle}.png")
    cv2.imwrite(demosaic_file, demosaiced_image)
    print(f"Demosaiced image saved: {demosaic_file}")

    # Convert to 10-bit (0-1023) for BSDF analysis
    demosaiced_image = np.round((demosaiced_image / 64).astype(np.uint16))
    print(f"Mean Intensity: {np.mean(demosaiced_image)}")

    # Extract individual color channels
    R, G, B = demosaiced_image[:, :, 2], demosaiced_image[:, :, 1], demosaiced_image[:, :, 0]
    print(f"Mean Intensity R: {np.mean(R)}")
    print(f"Mean Intensity G: {np.mean(G)}")
    print(f"Mean Intensity B: {np.mean(B)}")

    # Store BSDF-related intensity statistics
    bsdf_data.append({
        "Angle": angle,
        "Mean_Red": np.mean(R),
        "Mean_Green": np.mean(G),
        "Mean_Blue": np.mean(B),
        "Std_Red": np.std(R),
        "Std_Green": np.std(G),
        "Std_Blue": np.std(B),
        "Max_Red": np.max(R),
        "Max_Green": np.max(G),
        "Max_Blue": np.max(B),
        "Min_Red": np.min(R),
        "Min_Green": np.min(G),
        "Min_Blue": np.min(B),
    })

    # Plot Histogram of 10-bit pixel intensities
    plt.figure(figsize=(8, 6))
    plt.hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
    plt.hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
    plt.hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
    plt.title(f"Color Channel Histograms (10-bit) at {angle} Degrees")
    plt.xlabel("Pixel Intensity (0-1023)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot BSDF intensity map
    plt.figure(figsize=(8, 6))
    plt.imshow(demosaiced_image, cmap='inferno', aspect='auto')
    plt.colorbar(label="Pixel Intensity (0-1023)")
    plt.title(f"BSDF Heatmap at {angle} Degrees")
    plt.xlabel("X Pixels")
    plt.ylabel("Y Pixels")
    plt.show()

# Save BSDF data to a CSV
bsdf_df = pd.DataFrame(bsdf_data)
#bsdf_df = bsdf_df.round(2)
bsdf_file = os.path.join(processed_folder, "bsdf_data.csv")
bsdf_df.to_csv(bsdf_file, index=False)
print(f"BSDF data saved to {bsdf_file}")

# Stop camera
picam2.stop()
print("Capture sequence completed.")


