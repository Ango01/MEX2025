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

    return mean_val

def generate_zemax_bsdf_file(
    filename: str,
    symmetry: str,
    spectral_content: str,
    scatter_type: str,
    sample_rotations: list[int],
    incidence_angles: list[int],
    azimuth_angles: list[int],
    radial_angles: list[int],
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

