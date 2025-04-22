import rawpy, os, csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime

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
    G = (G1 + G2) / 2

    return R, G, B

def plot_intensity_histogram(image, angle):
    """Plot histogram of pixel intensities."""
    plt.figure()
    plt.hist(image.flatten(), bins=50, color='blue', alpha=0.7, edgecolor='black')
    plt.title(f"Pixel Intensity Distribution at {angle}°")
    plt.xlabel("Pixel Intensity (0-1023)")
    plt.ylabel("Frequency")
    plt.grid(True)

def plot_heatmap(image, angle, roi_diameter=20):
    """Plot heatmap of the RAW image with circular ROI overlay."""
    plt.figure()
    plt.imshow(image, cmap='inferno', aspect='auto')
    plt.colorbar(label="Pixel Intensity")
    plt.title(f"Heatmap of Scattered Light at {angle}°")

    # Center of the image
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2
    radius = roi_diameter / 2

    # Draw the ROI circle
    circle = patches.Circle((center_x, center_y), radius, edgecolor='red',
                            facecolor='none', linewidth=2)
    plt.gca().add_patch(circle)

def plot_color_heatmaps(R, G, B, angle):
    """Plot separate heatmaps for Red, Green, and Blue channels in 2D."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    axes[0].imshow(R, cmap='Reds', aspect='auto')
    axes[0].set_title(f"Red Channel at {angle}°")
    
    axes[1].imshow(G, cmap='Greens', aspect='auto')
    axes[1].set_title(f"Green Channel at {angle}°")
    
    axes[2].imshow(B, cmap='Blues', aspect='auto')
    axes[2].set_title(f"Blue Channel at {angle}°")

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

def compute_circular_roi_mean(image, diameter=20):
    """Compute the mean pixel value in a circular ROI at the center of the image."""
    radius = diameter // 2
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2

    y, x = np.ogrid[:image.shape[0], :image.shape[1]]
    mask = (x - center_x)**2 + (y - center_y)**2 <= radius**2
    roi_values = image[mask]

    N = len(roi_values)
    # Calculate mean intensity inside ROI which corresponds to constant*BRDF.
    mean_val = np.mean(roi_values)
    # Simple statistical analysis using 1-sigma
    std_val = np.std(roi_values)
    sigma = std_val / np.sqrt(N)

    return mean_val, sigma

def generate_zemax_bsdf_file(
    filename: str,
    symmetry: str,
    spectral_content: str,
    scatter_type: str,
    sample_rotations: list[float],
    incidence_angles: list[float],
    azimuth_angles: list[float],
    radial_angles: list[float],
    tis_data: dict,
    bsdf_data: dict,
):
    """
    Generates a Zemax Tabular BSDF file.

    Args:
        filename (str): Path to save the .BSDF file.
        symmetry (str): One of 'PlaneSymmetrical', 'Asymmetrical', 'Asymmetrical4D'.
        spectral_content (str): 'Monochrome' or 'XYZ'.
        scatter_type (str): 'BRDF' or 'BTDF'.
        sample_rotations (list): List of sample rotation angles.
        incidence_angles (list): List of angle of incidence values.
        azimuth_angles (list): List of azimuth angles.
        radial_angles (list): List of radial angles.
        tis_data (dict): TIS values, format: { (rot, inc): TIS_value }
        bsdf_data (dict): BSDF values, format: { (rot, inc): 2D array [azimuth][radial] }
    """

    def format_line(values):
        return ' '.join(f"{v:.6f}" if isinstance(v, float) else str(v) for v in values)

    with open(filename, 'w') as f:
        f.write("# Zemax Tabular BSDF file generated via Python\n")
        f.write(f"# Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("Source Measured\n")
        f.write(f"Symmetry {symmetry}\n")
        f.write(f"SpectralContent {spectral_content}\n")
        f.write(f"ScatterType {scatter_type}\n")

        # Sample Rotations
        f.write(f"SampleRotation {len(sample_rotations)}\n")
        f.write(format_line(sample_rotations) + "\n")

        # Angles of Incidence
        f.write(f"AngleOfIncidence {len(incidence_angles)}\n")
        f.write(format_line(incidence_angles) + "\n")

        # Azimuth
        f.write(f"ScatterAzimuth {len(azimuth_angles)}\n")
        f.write(format_line(azimuth_angles) + "\n")

        # Radial
        f.write(f"ScatterRadial {len(radial_angles)}\n")
        f.write(format_line(radial_angles) + "\n\n")

        f.write(f"{spectral_content}\n")
        f.write("DataBegin\n")

        for rot in sample_rotations:
            for inc in incidence_angles:
                key = (rot, inc)
                tis_value = tis_data.get(key, 0.0)
                scatter_grid = bsdf_data.get(key)

                if scatter_grid is None:
                    raise ValueError(f"Missing BSDF data for rotation={rot}, incidence={inc}")

                f.write(f"TIS {tis_value:.6f}\n")

                for row in scatter_grid:
                    f.write(format_line(row) + "\n")

        f.write("DataEnd\n")




# Example usage
if __name__ == "__main__":
    image_path = "image_0.dng"
    processed_image = process_raw_image(image_path)
    roi_mean, sigma = compute_circular_roi_mean(processed_image)


    #Extract the three color channels and calculate mean intensity inside ROI 
    R, G, B = extract_color_channels(processed_image)
    R_mean = compute_circular_roi_mean(R)
    G_mean = compute_circular_roi_mean(G)
    B_mean = compute_circular_roi_mean(B)

    # Input data to BSDF file generation
    sample_rot = [0, 90]
    inc_angles = [20]
    azimuths = [0, 90, 180, 270]
    radials = [0, 30, 60, 90]

    tis = {
        (0, 20): 0.25,
        (90, 20): 0.30,
    }

    bsdf = {
        (0, 20): [
            [0.01, 0.02, 0.01, 0.00],
            [0.02, 0.05, 0.02, 0.01],
            [0.01, 0.03, 0.02, 0.01],
            [0.00, 0.01, 0.01, 0.00],
        ],
        (90, 20): [
            [0.00, 0.01, 0.00, 0.00],
            [0.01, 0.04, 0.01, 0.01],
            [0.01, 0.02, 0.01, 0.01],
            [0.00, 0.01, 0.01, 0.00],
        ]
    }

    # Generate bsdf file compatible with zemax
    generate_zemax_bsdf_file(
        "my_brdf_file.bsdf",
        symmetry="Asymmetrical4D",
        spectral_content="Monochrome",
        scatter_type="BRDF",
        sample_rotations=sample_rot,
        incidence_angles=inc_angles,
        azimuth_angles=azimuths,
        radial_angles=radials,
        tis_data=tis,
        bsdf_data=bsdf
    )

    
    # Plots such as heatmaps and histogram for both RAW image and R,G,B images
    angle = 10  # Example angle
    plot_intensity_histogram(processed_image, angle)
    plot_heatmap(processed_image, angle)
    plot_color_heatmaps(R, G, B, angle)
    plot_color_histogram(R, G, B, angle)
    plt.show()