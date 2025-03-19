import rawpy
import numpy as np
import cv2
import os
import csv
import matplotlib.pyplot as plt

def process_raw_image(image_path):
    """Load a RAW image, convert it to a 16-bit grayscale NumPy array."""
    with rawpy.imread(image_path) as raw:
        raw_image = raw.raw_image_visible.astype(np.uint16)  # Convert to 16-bit
    return raw_image

def plot_intensity_histogram(image, angle):
    """Plot histogram of pixel intensities."""
    plt.hist(image.flatten(), bins=50, color='blue', alpha=0.7, edgecolor='black')
    plt.title(f"Pixel Intensity Distribution at {angle}°")
    plt.xlabel("Pixel Intensity (0-1023)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

def plot_heatmap(image, angle):
    """Plot heatmap of the RAW image."""
    plt.imshow(image, cmap='inferno', aspect='auto')
    plt.colorbar(label="Pixel Intensity")
    plt.title(f"Heatmap of Scattered Light at {angle}°")
    plt.show()

def extract_intensity_data(image):
    """Extract key intensity values for BSDF analysis."""
    avg_intensity = np.mean(image)  # Mean intensity of the whole image
    max_intensity = np.max(image)  # Maximum intensity value
    min_intensity = np.min(image)  # Minimum intensity value
    return avg_intensity, max_intensity, min_intensity

def save_intensity_data(image_path, angle, measurement_type, output_csv="scattering_data.csv"):
    """Save intensity data into a CSV file for later BSDF analysis."""
    image = process_raw_image(image_path)
    avg_intensity, max_intensity, min_intensity = extract_intensity_data(image)

    file_exists = os.path.isfile(output_csv)
    with open(output_csv, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Measurement Type", "Angle", "Avg Intensity", "Max Intensity", "Min Intensity"])
        writer.writerow([measurement_type, angle, avg_intensity, max_intensity, min_intensity])

    print(f"Data saved for {measurement_type} at {angle}°")


# Example usage
if __name__ == "__main__":
    image_path = "Captured_Images/image_0.dng"
    angle = 10  # Example angle
    processed_image = process_raw_image(image_path)
    plot_intensity_histogram(processed_image, angle)
    plot_heatmap(processed_image, angle)
    save_intensity_data(image_path, angle)