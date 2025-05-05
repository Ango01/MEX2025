import numpy as np
import cv2
from skimage.measure import shannon_entropy

def extract_color_channels(image):
    """Extract Red, Green, and Blue color channels from a Bayer RAW image."""
    # Bayer pattern: SBGGR (Blue in top-left)
    B = image[0::2, 0::2]     # Blue pixels (even rows and even columns)
    G1 = image[0::2, 1::2]    # Green pixels (even rows, odd columns)
    G2 = image[1::2, 0::2]    # Green pixels (odd rows, even columns)
    R = image[1::2, 1::2]     # Red pixels (odd rows and odd columns)

    # Average the two green channels
    G = (G1 + G2) / 2

    return R, G, B

def circular_roi_mean(image, diameter=20):
    """Compute the mean pixel value and 1-sigma uncertainty within a circular ROI at the center of the image."""
    radius = diameter // 2
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2

    y, x = np.ogrid[:image.shape[0], :image.shape[1]]
    mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    roi_values = image[mask] # Extract pixel values within circular mask

    N = len(roi_values)
    # Calculate mean intensity inside ROI which corresponds to constant*BRDF.
    mean_val = np.mean(roi_values)
    # Simple statistical analysis using 1-sigma
    std_val = np.std(roi_values)
    sigma = std_val / np.sqrt(N) 
    relative_error = sigma/mean_val 

    return float(mean_val), float(relative_error)

def entropy_noise_check(image, entropy_threshold=3):
    gray = image.astype(np.float32) / 1023.0  # normalize to 0-1
    entropy = shannon_entropy(gray)
    print(f"Entropy Value: {entropy} \n")
    return entropy > entropy_threshold

def detect_static_noise(image):
    try:
        variance_check = local_variance_noise_check(image)
        entropy_check = entropy_noise_check(image)
        if variance_check or entropy_check:
            return True
        else:
            return False

    except Exception as e:
        print(f"Error during noise detection: {e}")
        return False

def local_variance_noise_check(image, var_threshold=100):
    image = cv2.resize(image, (256, 256))  # Normalize size

    blur = cv2.GaussianBlur(image, (5, 5), 0)
    diff = cv2.absdiff(image, blur)
    variance = np.var(diff)
    print(f"Variance Value: {variance}")

    return variance > var_threshold

