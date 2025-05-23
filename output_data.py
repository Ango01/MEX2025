import csv, os, logging
import numpy as np
from datetime import datetime

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
    """Generate a Zemax Tabular BSDF file."""
    def write_header(f):
        """Write file metadata and axis definitions for the BSDF format."""
        f.write("# Data Generated by Python BSDF Generator\n")
        f.write(f"# {datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')}\n")
        f.write("Source  Measured\n")
        f.write(f"Symmetry  {symmetry}\n")
        f.write(f"SpectralContent  {spectral_content}\n")
        f.write(f"ScatterType  {scatter_type}\n")

        # Axis definitions
        f.write(f"SampleRotation {len(sample_rotations)}\n")
        f.write("\t".join(map(str, sample_rotations)) + "\n")

        f.write(f"AngleOfIncidence  {len(incidence_angles)}\n")
        f.write("\t".join(map(str, incidence_angles)) + "\n")

        f.write(f"ScatterAzimuth {len(azimuth_angles)}\n")
        f.write("\t".join(map(str, azimuth_angles)) + "\n")

        f.write(f"ScatterRadial {len(radial_angles)}\n")
        f.write("\t".join(map(str, radial_angles)) + "\n\n")

    def write_data_block(f, component_index: int, label: str):
        """Write a block of BSDF data for a specific spectral content (R, G, or B)."""
        f.write(f"{label}\n")
        f.write("DataBegin\n")

        for rot in sample_rotations:
            for inc in incidence_angles:
                key = (rot, inc)
                tis = tis_data.get(key, 0.0)
                grid = bsdf_data.get(key)

                if grid is None:
                    raise ValueError(f"Missing BSDF data for rotation={rot}, incidence={inc}")

                f.write(f"TIS {tis:.2f}\n")

                # Write 2D grid for this rotation-incidence pair
                for row in grid:
                    line = []
                    for triple in row:
                        val = triple[component_index] if triple is not None else 0.0
                        line.append(f"{val:.3E}")
                    f.write("\t".join(line) + "\n")

        f.write("DataEnd\n\n")

    # Write the complete BSDF file
    with open(filename, 'w') as f:
        write_header(f)
        write_data_block(f, component_index=0, label="R")
        write_data_block(f, component_index=1, label="G")
        write_data_block(f, component_index=2, label="B")
    
    logging.info(f"BSDF data file saved to {filename}")

def save_relative_errors(app, output_folder, filename):
    """Save the relative errors to a CSV file."""
    os.makedirs(output_folder, exist_ok=True)
    filepath = os.path.join(output_folder, filename)

    try:
        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["light_az", "light_rad", "det_az", "det_rad", "r_err", "g_err", "b_err"])

            r_list, g_list, b_list = [], [], []

            for (light_az, light_rad, det_az, det_rad), (r_err, g_err, b_err) in app.relative_errors.items():
                writer.writerow([light_az, light_rad, det_az, det_rad, r_err, g_err, b_err])
                r_list.append(r_err)
                g_list.append(g_err)
                b_list.append(b_err)

            # Compute and write mean values
            mean_r = np.mean(r_list) if r_list else 0
            mean_g = np.mean(g_list) if g_list else 0
            mean_b = np.mean(b_list) if b_list else 0

            writer.writerow([])
            writer.writerow(["Mean", "", "", "", mean_r, mean_g, mean_b])

        logging.info(f"Relative errors saved to {filepath}")

    except Exception as e:
        logging.error(f"Error saving relative errors: {e}")