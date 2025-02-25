import numpy as np
import cv2

def normalize_image(image):
    """
    Normalize a 16-bit image to range 0-1.
    
    Args:
        image (np.ndarray): Input 16-bit image.
    
    Returns:
        np.ndarray: Normalized image.
    """
    return image.astype(np.float32) / 65535.0  # Normalizing to 0-1 range

def dark_frame_correction(image, dark_frame):
    """
    Apply dark frame correction by subtracting the dark frame from the image.
    
    Args:
        image (np.ndarray): Input 16-bit image.
        dark_frame (np.ndarray): Dark frame (already unpacked and processed as 16-bit).
    
    Returns:
        np.ndarray: Dark-frame-corrected image.
    """
    return np.clip(image - dark_frame, 0, 65535)  # Maintain 16-bit depth

def flat_field_correction(image, flat_field):
    """
    Apply flat field correction by dividing by a uniform white field image.
    
    Args:
        image (np.ndarray): Input 16-bit image.
        flat_field (np.ndarray): Flat field reference image (already unpacked and processed as 16-bit).
    
    Returns:
        np.ndarray: Corrected image.
    """
    return np.clip((image / (flat_field + 1e-6)) * 65535, 0, 65535).astype(np.uint16)  # Maintain 16-bit depth

def preprocess_image(image_path, dark_frame_path, flat_field_path, output_path):
    """
    Preprocess an image by applying dark frame and flat field correction.
    
    Args:
        image_path (str): Path to the processed 16-bit image.
        dark_frame_path (str): Path to the dark frame image.
        flat_field_path (str): Path to the flat field image.
        output_path (str): Path to save the final preprocessed image.
    """
    # Load images as 16-bit grayscale
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED).astype(np.uint16)
    dark_frame = cv2.imread(dark_frame_path, cv2.IMREAD_UNCHANGED).astype(np.uint16)
    flat_field = cv2.imread(flat_field_path, cv2.IMREAD_UNCHANGED).astype(np.uint16)
    
    # Apply corrections
    image_corrected = dark_frame_correction(image, dark_frame)
    image_corrected = flat_field_correction(image_corrected, flat_field)
    
    # Save the final preprocessed image
    cv2.imwrite(output_path, image_corrected)  # Save as 16-bit
    
    print(f"Final preprocessed image saved to {output_path}")

# Example execution
if __name__ == "__main__":
    preprocess_image("processed_image.png", "dark_image.png", "flat_field.png", "final_preprocessed_image.png")
