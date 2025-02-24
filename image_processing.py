import cv2
import numpy as np

def preprocess_image(image):
    """Apply preprocessing to the loaded image (e.g., normalization, filtering)."""
    # Normalize image to 0-1 range
    image = image.astype(np.float32) / 255.0
    
    # Apply a Gaussian blur (optional)
    processed_image = cv2.GaussianBlur(image, (5, 5), 0)
    
    return processed_image

def compute_bsdf(image):
    """Compute a basic BSDF approximation using reflection and transmission."""
    if image is None:
        raise ValueError("No image data provided for BSDF computation.")

    # Compute reflection and transmission approximations
    reflection = np.mean(image[:100, :])  # Example: Top part
    transmission = np.mean(image[-100:, :])  # Example: Bottom part
    
    # Compute BSDF value (basic formula)
    bsdf_value = reflection / (transmission + 1e-6)  # Avoid division by zero

    return bsdf_value

