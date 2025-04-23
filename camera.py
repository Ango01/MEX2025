from picamera2 import Picamera2
import time

def initialize_camera():
  """Initialize and configure Picamera2 for RAW10 capture."""
  picam2 = Picamera2()
  config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
  picam2.configure(config)
        
  picam2.set_controls({
    "ExposureTime": 50,  
    "AnalogueGain": 1.0,
    "AeEnable": False,
    "AwbEnable": False,
  }) 

  picam2.start()
  time.sleep(2)  # Allow camera to stabilize (should be removed and substituted with a thread that listens to camera commands)

  return picam2  # Return the camera instance

def stop_camera(picam2):
  """Stop the camera."""
  if picam2:
    picam2.stop()
