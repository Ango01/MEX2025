import rawpy, os, csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def process_raw_image(image_path):
    """Load a RAW image, convert it to a 16-bit grayscale NumPy array."""
    with rawpy.imread(image_path) as raw:
        raw_image = raw.raw_image_visible.astype(np.uint16)  
    return raw_image

def extract_color_channels(image):
    """Extract Red, Green, and Blue color channels from a Bayer RAW image."""
    # Bayer pattern: SBGGR (Blue in top-left)
    B = image[0::2, 0::2]     # Blue pixels (every 2nd row, every 2nd column)
    G1 = image[0::2, 1::2]    # Green pixels (row 1, col 2)
    G2 = image[1::2, 0::2]    # Green pixels (row 2, col 1)
    R = image[1::2, 1::2]     # Red pixels (every 2nd row, every 2nd column)

    # Combine both Green channels
    G = G1 + G2 / 2

    return R, G, B

def compute_bsdf(brdf_file, btdf_file, output_file="scattering_data_bsdf.csv"):
    """Compute BSDF by summing BRDF and BTDF datasets."""
    df_brdf = pd.read_csv(brdf_file)
    df_btdf = pd.read_csv(btdf_file)
    df_bsdf = df_brdf.copy()
    df_bsdf[["Avg R Intensity", "Avg G Intensity", "Avg B Intensity"]] += df_btdf[["Avg R Intensity", "Avg G Intensity", "Avg B Intensity"]]
    df_bsdf.to_csv(output_file, index=False)
    print("BSDF dataset saved successfully!")

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

def plot_color_heatmaps(R, G, B, angle):
    """Plot separate heatmaps for Red, Green, and Blue channels in 2D."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    axes[0].imshow(R, cmap='Reds', aspect='auto')
    axes[0].set_title(f"Red Channel at {angle}°")
    
    axes[1].imshow(G, cmap='Greens', aspect='auto')
    axes[1].set_title(f"Green Channel at {angle}°")
    
    axes[2].imshow(B, cmap='Blues', aspect='auto')
    axes[2].set_title(f"Blue Channel at {angle}°")
    
    plt.show()

def plot_color_histogram(R, G, B, angle):
    """Plot histograms for Red, Green, and Blue channels together."""
    plt.figure(figsize=(8, 6))
    plt.hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
    plt.hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
    plt.hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
    plt.title(f"Color Channel Histograms at {angle}°")
    plt.xlabel("Pixel Intensity")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage
if __name__ == "__main__":
    image_path = "Captured_Images/image_0.dng"
    angle = 10  # Example angle
    processed_image = process_raw_image(image_path)
    plot_intensity_histogram(processed_image, angle)
    plot_heatmap(processed_image, angle)
    R, G, B = extract_color_channels(processed_image)
    plot_color_heatmaps(R, G, B, angle)
    plot_color_histogram(R, G, B, angle)