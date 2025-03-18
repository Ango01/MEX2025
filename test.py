
from picamera2 import Picamera2
import time
import numpy as np
import rawpy
import cv2
import matplotlib.pyplot as plt
import os
import pandas as pd

# Initialize camera
picam2 = Picamera2()

# Configure RAW10 capture
config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
picam2.configure(config)

picam2.set_controls({
    "ExposureTime": 5000,   # Set exposure time (in microseconds)
    "AnalogueGain": 1.0,    # Set gain to 1.0 (no artificial brightness boost)
    "AeEnable": False,      # Disable auto-exposure
    "AwbEnable": False,     # Disable auto white balance
})

input_folder = "Captured_Images"

picam2.start()
time.sleep(1)  # Allow camera to warm up


