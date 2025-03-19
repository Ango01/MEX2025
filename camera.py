from picamera2 import Picamera2
import time

def initialize_camera(exposure):
  """Initialize and configure Picamera2 for RAW10 capture."""

  # Initialize camera
  picam2 = Picamera2()
   
  # Configure RAW10 capture
  config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
  picam2.configure(config)
  
  # Set exposure and disable auto settings
  picam2.set_controls({
    "ExposureTime": int(exposure),  # Set exposure time (in microseconds)
    "AnalogueGain": 1.0,            # No artificial brightness boost
    "AeEnable": False,              # Disable auto-exposure
    "AwbEnable": False,             # Disable auto white balance
  }) 

  picam2.start()
  time.sleep(1) # Allow camera to stabilize

  print("Camera initialized and ready.")
  return picam2 # Return camera object