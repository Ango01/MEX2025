from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import matplotlib.pyplot as plt
import os
from scipy.optimize import curve_fit

def two_d_gaussian(coords, amplitude, xo, yo, sigma_x, sigma_y, offset):
    x, y = coords
    xo = float(xo)
    yo = float(yo)
    g = offset + amplitude * np.exp(
        -(((x - xo) ** 2) / (2 * sigma_x ** 2) + ((y - yo) ** 2) / (2 * sigma_y ** 2))
    )
    return g.ravel()

# Initialize camera
picam2 = Picamera2()
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

# Manual camera controls
picam2.set_controls({
    "ExposureTime": 5000,
    "AnalogueGain": 1.0,
    "AeEnable": False,
    "AwbEnable": False,
})

angles = range(0, 10, 10)  # Capture images every 10 degrees
output_folder = "Captured_Images"
os.makedirs(output_folder, exist_ok=True)

picam2.start()
time.sleep(1)  # Camera warm-up

# Store scattering results
scattering_results = {}

for angle in angles:
    input(f"Press Enter to capture image at {angle} degrees...")
    image_file = os.path.join(output_folder, f"image_{angle}.dng")
    picam2.capture_file(image_file, name="raw")
    print(f"Captured image at {angle} degrees")

    # Load RAW image
    with rawpy.imread(image_file) as raw:
        raw_image = raw.raw_image_visible.astype(np.uint16)

    # Extract Bayer channels (SBGGR10)
    B = raw_image[0::2, 0::2]     # Blue
    G1 = raw_image[0::2, 1::2]    # Green 1
    G2 = raw_image[1::2, 0::2]    # Green 2
    R = raw_image[1::2, 1::2]     # Red

    G = np.concatenate((G1.flatten(), G2.flatten()))

    # Compute integrated intensities
    R_sum = np.sum(R)
    G_sum = np.sum(G)
    B_sum = np.sum(B)
    total = R_sum + G_sum + B_sum

    scattering_results[angle] = {
        "Red": R_sum,
        "Green": G_sum,
        "Blue": B_sum,
        "R/G": R_sum / G_sum,
        "B/G": B_sum / G_sum,
        "Rel_R": R_sum / total,
        "Rel_G": G_sum / total,
        "Rel_B": B_sum / total
    }

    print(f"Angle {angle}° - R: {R_sum}, G: {G_sum}, B: {B_sum}")
    print(f"Relative intensities - R: {R_sum / total:.2f}, G: {G_sum / total:.2f}, B: {B_sum / total:.2f}")

    # Plot 2D heatmaps
    for channel, data, cmap in zip(["Red", "Green1", "Green2", "Blue"], [R, G1, G2, B], ["Reds", "Greens", "Greens", "Blues"]):
        plt.figure(figsize=(8, 6))
        plt.imshow(data, cmap=cmap, aspect='auto')
        plt.title(f"{channel} Channel Heatmap at {angle}°")
        plt.colorbar(label="Pixel Intensity (0-1023)")
        plt.xlabel("X Pixels")
        plt.ylabel("Y Pixels")
        plt.show()
    
    for channel_name, channel_data in zip(["Red", "Green", "Blue"], [R, G, B]):
        # Create X, Y meshgrid
        y_indices, x_indices = np.indices(channel_data.shape)

        # Initial guess for the parameters
        initial_guess = (
            np.max(channel_data),               # amplitude
            channel_data.shape[1] / 2,          # xo
            channel_data.shape[0] / 2,          # yo
            channel_data.shape[1] / 4,          # sigma_x
            channel_data.shape[0] / 4,          # sigma_y
            np.min(channel_data)                # offset
        )

        try:
            popt, _ = curve_fit(
                two_d_gaussian,
                (x_indices, y_indices),
                channel_data.ravel(),
                p0=initial_guess,
                maxfev=5000
            )

            data_fitted = two_d_gaussian((x_indices, y_indices), *popt).reshape(channel_data.shape)

            # Plot original + fitted surface
            plt.figure(figsize=(12, 5))

            plt.subplot(1, 2, 1)
            plt.imshow(channel_data, cmap='viridis', aspect='auto')
            plt.title(f"{channel_name} Channel - Raw Data at {angle}°")
            plt.colorbar()

            plt.subplot(1, 2, 2)
            plt.imshow(data_fitted, cmap='viridis', aspect='auto')
            plt.title(f"{channel_name} Channel - 2D Gaussian Fit at {angle}°")
            plt.colorbar()

            plt.tight_layout()
            plt.show()

        except RuntimeError:
            print(f"Could not fit 2D Gaussian to {channel_name} channel at {angle}°")

picam2.stop()

# ---- Plot intensity vs. angle ----
angles = sorted(scattering_results.keys())
red_vals = [scattering_results[a]["Red"] for a in angles]
green_vals = [scattering_results[a]["Green"] for a in angles]
blue_vals = [scattering_results[a]["Blue"] for a in angles]

plt.figure(figsize=(10, 6))
plt.plot(angles, red_vals, 'r-o', label="Red")
plt.plot(angles, green_vals, 'g-o', label="Green")
plt.plot(angles, blue_vals, 'b-o', label="Blue")
plt.xlabel("Scattering Angle (degrees)")
plt.ylabel("Integrated Intensity (sum of pixel values)")
plt.title("Scattering Intensity vs. Angle")
plt.legend()
plt.grid(True)
plt.show()