import rawpy
import imageio
import cv2
import numpy as np
from skimage.measure import shannon_entropy
from skimage.color import rgb2gray
import os

def read_image(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".dng":
        with rawpy.imread(image_path) as raw:
            rgb = raw.postprocess()
    else:
        rgb = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if rgb is None:
            raise FileNotFoundError(f"Image not found or unsupported format: {image_path}")
        rgb = cv2.cvtColor(rgb, cv2.COLOR_BGR2RGB)

    # Konvertera till gråskala på samma sätt oavsett källa
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    return gray


def local_variance_noise_check(image_path, var_threshold=100):
    img = read_image(image_path)
    img = cv2.resize(img, (256, 256))  # Normalize size

    blur = cv2.GaussianBlur(img, (5, 5), 0)
    diff = cv2.absdiff(img, blur)
    variance = np.var(diff)
    print(f"Variance Value: {variance}")

    return variance > var_threshold

def entropy_noise_check(image_path, entropy_threshold=3):
    img = read_image(image_path)
    gray = img.astype(np.float32) / 255.0  # normalize to 0-1
    entropy = shannon_entropy(gray)
    print(f"Entropy Value: {entropy} \n")
    return entropy > entropy_threshold

def detect_static_noise(image_path):
    try:
        variance_check = local_variance_noise_check(image_path)
        entropy_check = entropy_noise_check(image_path)
        if(variance_check or entropy_check):
            print("Throw Image")

    except FileNotFoundError as e:
        print(e)
        return False

# Example usage
if __name__ == "__main__":
    result = detect_static_noise("a0389860651_16.jpg")
    result = detect_static_noise("static1.jpg")
    result = detect_static_noise("image_0.dng")
    result = detect_static_noise("image_10.dng")
    result = detect_static_noise("image_20.dng")
    result = detect_static_noise("image_30.dng")
    result = detect_static_noise("test1.jpg")
    result = detect_static_noise("test2.jpg")
    result = detect_static_noise("test3.jpg")
    result = detect_static_noise("test4.jpg")
    result = detect_static_noise("test10.jpg")
