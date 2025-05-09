import cv2, logging
import numpy as np
from skimage.measure import shannon_entropy

def extract_color_channels(image):
    """Extract Red, Green, and Blue color channels from a Bayer RAW image."""
    # Bayer pattern: BGGR (Blue in top-left)
    B = image[0::2, 0::2]     # Blue pixels (even rows and even columns)
    G1 = image[0::2, 1::2]    # Green pixels (even rows, odd columns)
    G2 = image[1::2, 0::2]    # Green pixels (odd rows, even columns)
    R = image[1::2, 1::2]     # Red pixels (odd rows and odd columns)

    # Average two green channels
    G = (G1 + G2) / 2

    return R, G, B

def circular_roi_mean(image, diameter=20):
    """Compute the mean intensity and relative 1-sigma error within a circular ROI at image center."""
    radius = diameter // 2
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2
    
    # Create circular mask around center
    y, x = np.ogrid[:image.shape[0], :image.shape[1]]
    mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    roi_values = image[mask] # Extract pixel values within ROI

    # Mean and error estimation
    N = len(roi_values)
    mean_val = np.mean(roi_values) # TODO: constant*BRDF
    std_val = np.std(roi_values)
    sigma = std_val / np.sqrt(N) 
    relative_error = sigma / mean_val 

    return float(mean_val), float(relative_error)

def entropy_noise_check(image, entropy_threshold=3):
    """Use Shannon entropy to detect noise. Low entropy reflects static noise."""
    gray = image.astype(np.float32) / 1023.0  # Normalize to [0, 1]
    entropy = shannon_entropy(gray)
    logging.info(f"Entropy Value: {entropy} \n")

    # Return True if entropy suggests noise
    return entropy > entropy_threshold

def local_variance_noise_check(image, var_threshold=100):
    """Check local variance of image to detect static noise."""
    image = cv2.resize(image, (256, 256))  # Standardize resolution
    blur = cv2.GaussianBlur(image, (5, 5), 0) # Blur to remove detail
    diff = cv2.absdiff(image, blur) # Highlight fine noise
    variance = np.var(diff)

    logging.info(f"Variance Value: {variance}")

    # Return True if variance exceed threshold (image has structure)
    return variance > var_threshold

def detect_static_noise(image):
    """Noise check using local variance and entropy."""
    try:
        variance_check = local_variance_noise_check(image)
        entropy_check = entropy_noise_check(image)
        
        # Return True if either method detects static noise
        return variance_check or entropy_check

    except Exception as e:
        logging.error(f"Error during noise detection: {e}")
        return False