import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import center_of_mass
import subprocess

def unpack_raw10(data, width, height):
    """
    Unpacks RAW10 image data to 2D numpy array.
    """
    row_stride = width * 10 // 8
    raw10 = np.frombuffer(data, dtype=np.uint8)
    raw10 = raw10.reshape((height, row_stride))

    unpacked = np.zeros((height, width), dtype=np.uint16)

    for row in range(height):
        for col in range(0, width, 4):
            i = col * 10 // 8
            b = raw10[row, i:i+5]

            unpacked[row, col + 0] = (b[0] << 2) | ((b[4] >> 0) & 0x03)
            unpacked[row, col + 1] = (b[1] << 2) | ((b[4] >> 2) & 0x03)
            unpacked[row, col + 2] = (b[2] << 2) | ((b[4] >> 4) & 0x03)
            unpacked[row, col + 3] = (b[3] << 2) | ((b[4] >> 6) & 0x03)

    return unpacked

def find_spot_center(image, threshold_ratio=0.5):
    """
    Finds the center of the scattering spot using intensity thresholding and center of mass.
    """
    max_val = image.max()
    threshold = max_val * threshold_ratio
    mask = image > threshold
    center = center_of_mass(mask.astype(np.uint8))
    return center  # returns (y, x)

def radial_profile(image, center, bins=100):
    """
    Computes radial intensity profile from center.
    """
    y, x = np.indices(image.shape)
    r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
    r = r.astype(np.int32)

    max_radius = r.max()
    r = np.clip(r, 0, bins - 1)

    profile = np.bincount(r.ravel(), image.ravel()) / np.bincount(r.ravel())
    return profile

def plot_radial_profile(profile):
    plt.figure()
    plt.plot(profile)
    plt.title("Radial Intensity Profile")
    plt.xlabel("Radius (pixels)")
    plt.ylabel("Average Intensity")
    plt.grid()
    plt.show()

def capture_raw_image(filename="image", width=1456, height=1088, shutter=10000):
    """
    Captures a raw image using libcamera-still and saves it to filename.raw
    """
    cmd = [
        "libcamera-still",
        "-o", f"{filename}.jpg",
        "--raw",
        "--width", str(width),
        "--height", str(height),
        "--shutter", str(shutter),
        "--gain", "1",
        "--awbgains", "1,1",
        "--nopreview",
        "-n"
    ]
    subprocess.run(cmd, check=True)

def read_raw10_image(filepath, width, height):
    """
    Reads a RAW10 file and returns the unpacked image as a NumPy array.
    """
    with open(filepath, "rb") as f:
        raw_data = f.read()
    image = unpack_raw10(raw_data, width, height)
    return image


# Assume `raw_data` is your raw image bytes
width, height = 1456, 1088  # change to match your camera config
capture_raw_image()
raw_image = read_raw10_image("image.jpg.raw", width, height)
raw_img = unpack_raw10(raw_image, width, height)

center = find_spot_center(raw_img)
profile = radial_profile(raw_img, center)

plot_radial_profile(profile)