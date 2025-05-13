from picamera2 import Picamera2
import time
import numpy as np
import os
import matplotlib.pyplot as plt

# ======== Plotting Functions ========

def plot_pixel_histogram(pixel_values, angle):
    plt.figure(figsize=(8, 6))
    plt.hist(pixel_values, bins=50, color='blue', alpha=0.7, edgecolor='black')
    plt.title(f"Pixel Intensity Histogram at {angle}°")
    plt.xlabel("Pixel Intensity (0-1023)")
    plt.ylabel("Frequency")
    plt.grid(True)
    plt.show()

def plot_heatmap(raw_array, angle):
    plt.figure(figsize=(8, 6))
    plt.imshow(raw_array, cmap='inferno', aspect='auto')
    plt.colorbar(label="Pixel Intensity (0-1023)")
    plt.title(f"Heatmap of RAW Image at {angle}°")
    plt.xlabel("X Pixels")
    plt.ylabel("Y Pixels")
    plt.show()

def plot_color_histograms(R, G, B, angle):
    plt.figure(figsize=(8, 6))
    plt.hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
    plt.hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
    plt.hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
    plt.title(f"Color Channel Histograms at {angle}°")
    plt.xlabel("Pixel Intensity (0-1023)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)
    plt.show()
  
def capture_exposure_curve(picam2, output_folder, start_us, step_us, count):
    actual_exposures = []
    mean_intensities = []

    for i in range(count):
        intended_exp = start_us + i * step_us
        print(f"\nSetting exposure time to {intended_exp} µs...")

        # Set exposure manually
        picam2.set_controls({"ExposureTime": intended_exp})
        time.sleep(5)  # Allow time for settings to apply

        input(f"Press Enter to capture image at {intended_exp} µs...")

        raw = picam2.capture_array("raw")
        print(raw.dtype, raw.shape)

        raw_array = picam2.capture_array("raw").view(np.uint16)
        print(raw_array.dtype, raw_array.shape)
        print(f"Min: {np.min(raw_array)}, Max: {np.max(raw_array)}")

        image_filename = f"heatmap_histogram_{intended_exp}us.png"
        save_path = os.path.join(output_folder, image_filename)
        plot_heatmap_and_histogram(raw_array, save_path)

        mean_intensity = np.mean(raw_array)
        mean_intensities.append(mean_intensity)

        actual_exp = picam2.capture_metadata().get("ExposureTime", intended_exp)
        actual_exposures.append(actual_exp)

        print(f"Captured. Mean intensity: {mean_intensity:.2f}")
        print(f"Actual ExposureTime from metadata: {actual_exp} µs")

    # Plot curve
    plt.figure(figsize=(8, 6))
    plt.plot(actual_exposures, mean_intensities, marker='o', color='blue')
    plt.title("Exposure Time vs Mean Pixel Intensity")
    plt.xlabel("Exposure Time (µs)")
    plt.ylabel("Mean Pixel Intensity (0-1023)")
    plt.grid(True)

    plot_path = os.path.join(output_folder, "exposure_vs_intensity_higher_power_2.png")
    plt.savefig(plot_path)
    plt.show()
    print(f"Saved exposure curve to {plot_path}")

def plot_heatmap_and_histogram(raw_array, save_path):

    fig, axs = plt.subplots(1, 2, figsize=(14, 6))

    # --- Heatmap (left) ---
    im = axs[0].imshow(raw_array, cmap='inferno', aspect='auto')
    axs[0].set_title(f"Heatmap")
    axs[0].set_xlabel("X Pixels")
    axs[0].set_ylabel("Y Pixels")
    fig.colorbar(im, ax=axs[0], fraction=0.046, pad=0.04, label="Pixel Intensity")

    # --- Extract SBGGR10 Bayer Pattern Channels ---
    B = raw_array[0::2, 0::2]     # Blue
    G1 = raw_array[0::2, 1::2]    # Green 1
    G2 = raw_array[1::2, 0::2]    # Green 2
    R = raw_array[1::2, 1::2]     # Red
    G = (G1 + G2) / 2             # Average Green

    # --- Color Channel Histograms (right) ---
    axs[1].hist(R.flatten(), bins=50, color='red', alpha=0.6, label="Red", edgecolor='black')
    axs[1].hist(G.flatten(), bins=50, color='green', alpha=0.6, label="Green", edgecolor='black')
    axs[1].hist(B.flatten(), bins=50, color='blue', alpha=0.6, label="Blue", edgecolor='black')
    axs[1].set_title(f"Color Channel Histogram")
    axs[1].set_xlabel("Pixel Intensity (0-1023)")
    axs[1].set_ylabel("Frequency")
    axs[1].legend()
    axs[1].grid(True)

    plt.tight_layout()
    plt.savefig(save_path)
    plt.show()
    print(f"Saved heatmap + color channel histogram to {save_path}")


# ======== Main Program ========

def main():
    picam2 = Picamera2()
    config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
    picam2.configure(config)

    picam2.start()
    time.sleep(1)

    picam2.set_controls({
    "AeEnable": False,
    "AnalogueGain": 1.0,
    "AwbEnable": False
})

    time.sleep(1)

    output_folder = "Captured_Images"
    os.makedirs(output_folder, exist_ok=True)

    #angles = range(0, 1, 1)  

    #for angle in angles:
    #    input(f"Press Enter to capture image at {angle} degrees...")

    #    raw_array = picam2.capture_array("raw").view(np.uint16)

    #    print(f"Shape: {raw_array.shape}")
    #    print(f"Dtype: {raw_array.dtype}")
    #    print(f"Min/Max: {raw_array.min()} / {raw_array.max()}")
        
    #    print(f"Captured image at {angle} degrees")

    #    actual_exp = picam2.capture_metadata().get("ExposureTime", "N/A")
    #    print(f"Reported ExposureTime from metadata: {actual_exp} µs\n")

    #    save_path = os.path.join(output_folder, f"heatmap_histogram_test.png")
    #    plot_heatmap_and_histogram(raw_array, save_path)

    capture_exposure_curve(picam2, output_folder, start_us=30, step_us=1000, count=20)

    picam2.stop()
    print("Capture sequence completed.")

# ======== Run Main ========
if __name__ == "__main__":
    main()

