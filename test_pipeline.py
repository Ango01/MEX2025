import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
import subprocess
import rawpy
import os

# -----------------------------------------------------------
# STEP 1: Capture image using libcamera-still
# -----------------------------------------------------------
def capture_raw_image(filename="image", width=1456, height=1088, shutter=10000):
    """
    Captures a raw image using libcamera-still and saves it as a DNG file.
    """
    cmd = [
        "libcamera-still",
        "-o", f"{filename}.dng",         # Save as DNG
        "--rawfull",                     # Full RAW data
        "--width", str(width),
        "--height", str(height),
        "--shutter", str(shutter),
        "--gain", "1",
        "--awbgains", "1,1",
        "--nopreview",
        "-n"
    ]
    subprocess.run(cmd, check=True)

# -----------------------------------------------------------
# STEP 2: Read DNG image and return raw Bayer image
# -----------------------------------------------------------
def read_dng_image(filepath):
    """
    Reads a DNG image using rawpy and returns a 2D numpy array (monochrome).
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found. Check if the capture worked.")

    with rawpy.imread(filepath) as raw:
        bayer = raw.raw_image.copy().astype(np.uint16)
    return bayer

# -----------------------------------------------------------
# STEP 3: Find center of scattering spot
# -----------------------------------------------------------
from scipy.ndimage import center_of_mass

def find_spot_center(image, threshold_ratio=0.5):
    """
    Finds the center of the scattering spot using thresholding and center of mass.
    """
    max_val = image.max()
    threshold = max_val * threshold_ratio
    mask = image > threshold
    center = center_of_mass(mask.astype(np.uint8))
    return center  # (y, x)

# -----------------------------------------------------------
# STEP 4: Radial intensity profile
# -----------------------------------------------------------
def radial_profile(image, center, bins=500):
    """
    Computes radial intensity profile from center of the scattering pattern.
    """
    y, x = np.indices(image.shape)
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    r = r.astype(np.int32)
    r = np.clip(r, 0, bins - 1)

    profile = np.bincount(r.ravel(), image.ravel()) / np.bincount(r.ravel())
    return profile

# -----------------------------------------------------------
# STEP 5: Plotting the radial profile
# -----------------------------------------------------------
def plot_radial_profile(profile):
    plt.figure()
    plt.plot(profile)
    plt.title("Radial Intensity Profile")
    plt.xlabel("Radius (pixels)")
    plt.ylabel("Average Intensity")
    plt.grid()
    plt.tight_layout()
    plt.show()

# -----------------------------------------------------------
# STEP 6: Main Pipeline
# -----------------------------------------------------------
def main():
    width, height = 1456, 1088
    filename = "image"
    
    print("📸 Capturing RAW image...")
    capture_raw_image(filename=filename, width=width, height=height)

    print("📥 Reading and processing DNG image...")
    raw_img = read_dng_image(f"{filename}.dng")

    print("🎯 Finding spot center...")
    center = find_spot_center(raw_img)
    print(f"Center: (y={center[0]:.1f}, x={center[1]:.1f})")

    print("📊 Computing radial intensity profile...")
    profile = radial_profile(raw_img, center)

    print("📈 Plotting profile...")
    plot_radial_profile(profile)

if __name__ == "__main__":
    main()
