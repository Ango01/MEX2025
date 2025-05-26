from picamera2 import Picamera2
import time

def initialize_camera():
  """Initialize and configure Picamera2 for RAW10 capture."""
  # Create a Picamera2 instance
  picam2 = Picamera2()

  # Create a still image configuration with RAW10 format and specified resolution
  config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
  picam2.configure(config)

  # Start the camera
  picam2.start()
  time.sleep(1.0)

  picam2.set_controls({
    "ExposureTime": 100000,   # Set fixed exposure time (microseconds)
    "AeEnable": False,      # Disable auto-exposure
    "AwbEnable": False,     # Disable auto-white balance
    "AnalogueGain": 1.0,    # Set analog gain
  }) 

  time.sleep(2)  # TODO: should be removed and substituted with a thread that listens to camera commands

  return picam2  # Return the camera instance
