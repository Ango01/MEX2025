import numpy as np
import cv2
import os
from picamera2 import Picamera2

def visualize_roi(image, diameter=20, save_dir="Captured_Images", filename="roi_visualization.jpg"):
    """Draw a circular ROI on the image and save it."""
    os.makedirs(save_dir, exist_ok=True)

    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2
    radius = diameter // 2

    # Normalize and convert to 8-bit
    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    vis_image = normalized.astype(np.uint8)

    # Convert to 3-channel for color drawing
    vis_image = cv2.merge([vis_image]*3)

    # Draw circle
    cv2.circle(vis_image, (center_x, center_y), radius, (0, 0, 255), 1)

    # Save image
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, vis_image)
    logging.info(f"ROI visualization saved to {save_path}")

def main():

    # Initialize camera
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(raw={"format": "SRGGB10"}))
    picam2.start()
    
    # Wait for camera to warm up
    import time
    time.sleep(2)

    # Capture raw image
    raw_image = capture_raw_image(picam2)

    # Process ROI
    mean_val, rel_error = circular_roi_mean(raw_image)
    logging.info(f"ROI mean intensity: {mean_val:.2f}")
    logging.info(f"ROI relative 1-sigma error: {rel_error:.4f}")

    # Save visualization
    visualize_roi(raw_image, diameter=20)

if __name__ == "__main__":
    main()

