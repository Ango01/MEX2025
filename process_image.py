import rawpy, os, csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

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

