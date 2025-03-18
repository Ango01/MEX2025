import os
import rawpy
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Define input and output folders
input_folder = "Captured_Images"
output_folder = "Demosaiced_Images"
os.makedirs(output_folder, exist_ok=True)

# List all DNG files in the captured folder
dng_files = [f for f in os.listdir(input_folder) if f.endswith(".dng")]

# Process each captured RAW10 image
for image_file in dng_files:
    angle = image_file.split("_")[-1].split(".")[0]  # Extract angle from filename
    input_path = os.path.join(input_folder, image_file)
    output_path = os.path.join(output_folder, f"demosaiced_{angle}.png")

    print(f"Processing {image_file}...")

    # Open the DNG file using rawpy
    with rawpy.imread(input_path) as raw:
        # Perform demosaicing with high-quality processing
        demosaiced_image = raw.postprocess(
            use_camera_wb=False,  # Disable auto white balance
            no_auto_bright=True,  # Prevent brightness normalization
            gamma=(1, 1),         # Keep gamma correction neutral (linear)
            output_bps=16,        # Output as 16-bit to preserve detail
            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD  # Adaptive homogeneity-directed demosaicing
        )

    # Convert to 10-bit (0-1023) by scaling down
    demosaiced_image_10bit = np.round(demosaiced_image / 64).astype(np.uint16)

    # Save the demosaiced image
    cv2.imwrite(output_path, demosaiced_image_10bit)
    print(f"Saved: {output_path}")

    # Extract individual color channels
    R, G, B = demosaiced_image_10bit[:, :, 2], demosaiced_image_10bit[:, :, 1], demosaiced_image_10bit[:, :, 0]

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

    # Plot BSDF Heatmap
    plt.figure(figsize=(8, 6))
    plt.imshow(demosaiced_image_10bit, cmap='inferno', aspect='auto')
    plt.colorbar(label="Pixel Intensity (0-1023)")
    plt.title(f"BSDF Heatmap at {angle} Degrees")
    plt.xlabel("X Pixels")
    plt.ylabel("Y Pixels")
    plt.show()

print("Demosaicing process completed.")



