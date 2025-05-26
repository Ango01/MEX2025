import numpy as np
import cv2
import os
import time
import matplotlib.pyplot as plt
from picamera2 import Picamera2

def capture_raw_image(picam2):
    raw = picam2.capture_array("raw").view(np.uint16)
    actual_exp = picam2.capture_metadata().get("ExposureTime")
    print(f"Actual ExposureTime from metadata: {actual_exp} µs")
    print(f"Max pixel value: {np.max(raw)}")
    #print(f"Datatype: {raw.dtype}")
    #print(f"Size: {raw.shape}")
    return raw

def check_and_adjust_exposure(picam2, image, angle, target_min=818, target_max=921, max_attempts=5):
    """
    Iteratively adjust exposure until the mean of the top 5% brightest pixels
    in the dominant channel is within target range.
    """
    attempt = 0
    while attempt < max_attempts:
        R, G, B = extract_color_channels(image)

        # Determine dominant channel
        channel_means = {'R': np.mean(R), 'G': np.mean(G), 'B': np.mean(B)}
        dominant = max(channel_means, key=channel_means.get)
        channel_data = {'R': R, 'G': G, 'B': B}[dominant]

        # Compute top 5% threshold and stats
        flat = channel_data.flatten()
        cutoff = int(len(flat) * 0.05)
        top_pixels = np.sort(flat)[-cutoff:]
        top_mean = np.mean(top_pixels)
        top_median = np.median(top_pixels)
        threshold_value = np.sort(flat)[-cutoff]

        print(f"\n[Attempt {attempt + 1}] Dominant: {dominant}, Top 5% mean: {top_mean:.2f}, Threshold: {threshold_value:.2f}")
        plot_color_histogram(R, G, B, angle, stage=f"attempt_{attempt+1}", 
                             dominant_channel=dominant, top5_threshold=threshold_value)

        if target_min <= top_mean <= target_max:
            print("Exposure is acceptable.\n")
            return image # Done

        # Adjust exposure
        metadata = picam2.capture_metadata()
        current_exp = metadata.get("ExposureTime", 10000)
        target_mid = (target_min + target_max) / 2
        diff_ratio = (top_mean - target_mid) / target_mid
        scaling_factor = 0.15  # Increase if convergence is too slow
        base_step = max(100, int(current_exp * scaling_factor * abs(diff_ratio)))

        if top_mean > target_max:
            new_exp = max(current_exp - base_step, 100)
            print(f"Too bright → Decreasing exposure by {base_step} µs")
        else:
            new_exp = current_exp + base_step
            print(f"Too dark → Increasing exposure by {base_step} µs")

        print(f"Adjusting exposure: {current_exp} → {new_exp}\n")
        picam2.set_controls({"ExposureTime": int(new_exp)})
        time.sleep(1)

        # Capture new image for next check
        image = picam2.capture_array("raw").view(np.uint16)
        attempt += 1

    print("Max attempts reached. Exposure may still be out of range.")
    return image

def extract_color_channels(image):
    """Extract Red, Green, and Blue color channels from a Bayer RAW image (BGGR)."""
    B = image[0::2, 0::2]
    G1 = image[0::2, 1::2]
    G2 = image[1::2, 0::2]
    R = image[1::2, 1::2]
    G = (G1 + G2) / 2
    #print(f"B: {B.shape}, R: {R.shape}, G: {G.shape}")
    return R, G, B

def plot_color_histogram(R, G, B, angle, stage="before", dominant_channel=None, top5_threshold=None):
    """Save a plot of R, G, B channel intensities and mark top 5% of the dominant channel."""
    plt.figure()

    # Plot histograms
    plt.hist(R.flatten(), bins=256, alpha=0.5, label="R", color="red")
    plt.hist(G.flatten(), bins=256, alpha=0.5, label="G", color="green")
    plt.hist(B.flatten(), bins=256, alpha=0.5, label="B", color="blue")

    # Highlight top 5% of dominant channel if provided
    if dominant_channel and top5_threshold is not None:
        channel_data = {'R': R, 'G': G, 'B': B}[dominant_channel].flatten()
        cutoff_value = np.percentile(channel_data, 95)
        plt.axvline(cutoff_value, color="black", linestyle="--", linewidth=1.5, label=f"95th %ile ({dominant_channel})")
        plt.axvspan(cutoff_value, channel_data.max(), color='gray', alpha=0.3)

    # Labels and save
    plt.title(f"Color Histogram ({stage} exposure adj) - Angle {angle}°")
    plt.xlabel("Intensity")
    plt.ylabel("Pixel Count")
    plt.legend()
    os.makedirs("Exposure_Histograms", exist_ok=True)
    plt.savefig(f"Exposure_Histograms/angle_{angle}_{stage}.png")
    plt.close()


def circular_roi_mean(image, diameter=20):
    """Compute mean intensity and relative 1-sigma error in the ROI for each color channel."""
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2
    radius = diameter // 2

    # Extract color channels
    R, G, B = extract_color_channels(image)

    # Get center and mask per channel size
    def get_mask(channel):
        ch_y, ch_x = channel.shape
        y, x = np.ogrid[:ch_y, :ch_x]
        cy, cx = ch_y // 2, ch_x // 2
        return (x - cx)**2 + (y - cy)**2 <= (radius // 2)**2  # radius scaled for subsampled channels

    R_roi = R[get_mask(R)]
    G_roi = G[get_mask(G)]
    B_roi = B[get_mask(B)]

    stats = {}
    for channel, data in zip(['R', 'G', 'B'], [R_roi, G_roi, B_roi]):
        mean_val = np.mean(data)
        rel_error = np.std(data) / mean_val if mean_val != 0 else 0
        stats[channel] = (mean_val, rel_error)

    return stats

def visualize_roi(image, diameter=20, save_dir="Captured_Images_4", filename="roi_visualization.jpg"):
    os.makedirs(save_dir, exist_ok=True)
    center_y, center_x = image.shape[0] // 2, image.shape[1] // 2
    radius = diameter // 2
    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    vis_image = normalized.astype(np.uint8)
    vis_image = cv2.merge([vis_image]*3)
    cv2.circle(vis_image, (center_x, center_y), radius, (0, 0, 255), 1)
    save_path = os.path.join(save_dir, filename)
    cv2.imwrite(save_path, vis_image)
    print(f"ROI visualization saved to {save_path}")

def main():
    picam2 = Picamera2()
    picam2.configure(picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)}))
    picam2.start()
    picam2.set_controls({
        "ExposureTime": 500000,
        "AeEnable": False,
        "AnalogueGain": 1.0,
        "AwbEnable": False
    })
    time.sleep(2)

    angle = 0
    while True:
        user_input = input(f"Press Enter to capture image at angle {angle}° (or type 'q' to quit): ")
        if user_input.lower() == 'q':
            break

        raw_image = capture_raw_image(picam2)

        # Check and adjust exposure
        #raw_image = check_and_adjust_exposure(picam2, raw_image, angle)
        actual_exp = picam2.capture_metadata().get("ExposureTime")
        print(f"Actual ExposureTime from metadata: {actual_exp} µs")

        # Save raw image as PNG (normalized for viewing)
        os.makedirs("Captured_Images_4", exist_ok=True)
        png_filename = f"angle_{angle}_raw.png"
        png_path = os.path.join("Captured_Images_4", png_filename)
        normalized = cv2.normalize(raw_image, None, 0, 255, cv2.NORM_MINMAX)
        cv2.imwrite(png_path, normalized.astype(np.uint8))
        print(f"Saved normalized PNG to {png_path}")

        # Save raw image data as .npy
        npy_filename = f"angle_{angle}_raw.npy"
        npy_path = os.path.join("Captured_Images_4", npy_filename)
        np.save(npy_path, raw_image)
        print(f"Saved raw array to {npy_path}")


        roi_stats = circular_roi_mean(raw_image)
        print("ROI mean intensities and relative 1-sigma errors:")
        for channel, (mean_val, rel_error) in roi_stats.items():
            print(f"  {channel}: Mean = {mean_val:.2f}, Rel. Error = {rel_error:.4f}")

        # Save ROI visualization
        vis_filename = f"angle_{angle}_roi.jpg"
        visualize_roi(raw_image, diameter=20, filename=vis_filename)

        angle += 10

if __name__ == "__main__":
    main()