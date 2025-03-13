import rawpy

# Load the DNG file
image_file = "Captured_Images/image_0.dng"
with rawpy.imread(image_file) as raw:
    raw_image = raw.raw_image_visible  # Extract the raw data
    print("Raw image data type:", raw_image.dtype)  # Check the NumPy data type

