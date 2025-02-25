import numpy as np
import cv2

def unpack_raw10(raw10_data, width, height):
    """
    Unpacks a RAW10 image into a 16-bit NumPy array.
    Each group of 4 pixels is stored in 5 bytes:
    - 4 most significant bytes store the upper 8 bits of each pixel.
    - The least significant 2 bits for each pixel are stored in the 5th byte.
    
    Args:
        raw10_data (bytes): The RAW10 image data.
        width (int): Image width.
        height (int): Image height.
    
    Returns:
        np.ndarray: 16-bit image with properly unpacked pixel values.
    """
    raw10_data = np.frombuffer(raw10_data, dtype=np.uint8)
    num_pixels = width * height
    
    # Reshape into 5-byte blocks
    raw10_data = raw10_data.reshape((-1, 5))
    
    # Extract the high 8 bits (first 4 bytes of each 5-byte block)
    high_bytes = raw10_data[:, :4].astype(np.uint16)  # Shape (-1, 4)
    
    # Extract the low 2 bits (5th byte)
    low_bytes = raw10_data[:, 4].astype(np.uint16)  # Shape (-1,)
    
    # Extract the actual pixel values
    pixels = (high_bytes << 2) | ((low_bytes[:, None] >> np.array([6, 4, 2, 0])) & 0x03)
    
    # Flatten and reshape into original image dimensions
    image = pixels.flatten().reshape((height, width))
    
    return image

# Example usage
def process_raw10_image(raw10_filename, width, height):
    """
    Reads a RAW10 file and processes it into a 16-bit image.
    
    Args:
        raw10_filename (str): Path to the RAW10 file.
        width (int): Image width.
        height (int): Image height.
    
    Returns:
        np.ndarray: Processed 16-bit image.
    """
    with open(raw10_filename, 'rb') as f:
        raw10_data = f.read()
    
    image_16bit = unpack_raw10(raw10_data, width, height)
    
    # Save the processed image as a 16-bit PNG (for visualization)
    cv2.imwrite('processed_image.png', image_16bit)
    
    return image_16bit

# Example execution (replace 'image.raw' with actual filename and set correct dimensions)
if __name__ == "__main__":
    width, height = 1456, 1088  # Set your camera's resolution
    processed_image = process_raw10_image('image.raw', width, height)
    print("RAW10 image successfully processed and saved as processed_image.png")

