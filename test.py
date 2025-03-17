import rawpy
import numpy as np

# Load your DNG file
dng_file = "Captured_Images/image_0.dng"  # Change based on your file
with rawpy.imread(dng_file) as raw:
    raw_image = raw.raw_image_visible.astype(np.uint16)  # Extract raw pixel data

# Print image details
print(f"Image Shape: {raw_image.shape}")  # Height, Width
print(f"Data Type: {raw_image.dtype}")  # Expected: uint16 (RAW10 stored in 16-bit container)
print(f"Min Pixel Value: {np.min(raw_image)}")  # Should be ≥ 0
print(f"Max Pixel Value: {np.max(raw_image)}")  # Should be ≤ 1023 for RAW10
