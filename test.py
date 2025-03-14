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
        raw_image = raw.raw_image_visible.astype(np.uint16)  # Raw Bayer image
        rgb_image = raw.postprocess(
            use_camera_wb=False,  
            half_size=False,      
            demosaic_algorithm=rawpy.DemosaicAlgorithm.AHD,  
            gamma=(1,1), # Disables gamma correction
            no_auto_bright=True,
        )

    # Convert raw Bayer image to grayscale for comparison
    raw_gray = cv2.normalize(raw_image, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Convert demosaiced RGB image to grayscale
    gray_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2GRAY)

    ## ---- Compare Histograms ---- ##
    plt.figure(figsize=(10, 5))
    plt.hist(raw_gray.flatten(), bins=50, color='gray', alpha=0.7, edgecolor='black', label="Raw Bayer")
    plt.hist(gray_image.flatten(), bins=50, color='blue', alpha=0.5, edgecolor='black', label="Demosaiced")
    plt.title(f"Comparison of Pixel Intensity Histograms at {angle} Degrees")
    plt.xlabel("Pixel Intensity (0-255)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

    ## ---- Compare Heatmaps ---- ##
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))

    ax[0].imshow(raw_gray, cmap='inferno', aspect='auto')
    ax[0].set_title(f"Raw Bayer Image at {angle}°")
    ax[0].set_xlabel("X Pixels")
    ax[0].set_ylabel("Y Pixels")

    ax[1].imshow(gray_image, cmap='inferno', aspect='auto')
    ax[1].set_title(f"Demosaiced Image at {angle}°")
    ax[1].set_xlabel("X Pixels")
    ax[1].set_ylabel("Y Pixels")

    plt.colorbar(ax[1].imshow(gray_image, cmap='inferno'), ax=ax[1], label="Pixel Intensity")
    plt.tight_layout()
    plt.show()

    ## ---- Extract & Compare Color Channels ---- ##
    red = rgb_image[:, :, 0]   
    green = rgb_image[:, :, 1] 
    blue = rgb_image[:, :, 2]  

    # Extract Bayer pattern channels (pre-demosaicing)
    raw_blue = raw_image[0::2, 0::2]    
    raw_green1 = raw_image[0::2, 1::2]  
    raw_green2 = raw_image[1::2, 0::2]  
    raw_red = raw_image[1::2, 1::2]     

    # Merge both green channels
    raw_green = np.concatenate((raw_green1.flatten(), raw_green2.flatten()))

    ## ---- Plot Histograms for Each Color ---- ##
    plt.figure(figsize=(10, 6))
    
    # Raw Bayer Histograms
    plt.hist(raw_red.flatten(), bins=50, color='red', alpha=0.4, label="Raw Red", edgecolor='black')
    plt.hist(raw_green.flatten(), bins=50, color='green', alpha=0.4, label="Raw Green", edgecolor='black')
    plt.hist(raw_blue.flatten(), bins=50, color='blue', alpha=0.4, label="Raw Blue", edgecolor='black')

    # Demosaiced Histograms
    plt.hist(red.flatten(), bins=50, color='red', alpha=0.6, label="Demosaiced Red", edgecolor='black')
    plt.hist(green.flatten(), bins=50, color='green', alpha=0.6, label="Demosaiced Green", edgecolor='black')
    plt.hist(blue.flatten(), bins=50, color='blue', alpha=0.6, label="Demosaiced Blue", edgecolor='black')

    plt.title(f"Color Channel Histograms at {angle} Degrees (Raw vs. Demosaiced)")
    plt.xlabel("Pixel Intensity (0-255)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

picam2.stop()
print("Capture sequence completed.")
