from picamera2 import Picamera2
import time

def initialize_camera():
  """Initialize and configure Picamera2 for RAW10 capture."""
  try:
    picam2 = Picamera2()
    config = picam2.create_still_configuration(raw={"format": "SRGGB10", "size": (1456, 1088)})
    picam2.configure(config)
        
    picam2.set_controls({
      "ExposureTime": 5000,  
      "AnalogueGain": 1.0,
      "AeEnable": False,
      "AwbEnable": False,
    }) 

    picam2.start()
    time.sleep(2)  # Allow camera to stabilize (should be removed and substituted with a thread that listens to camera commands)

    print("Camera initialized and ready.")
    return picam2  # Return the camera instance

  except Exception as e:
    print(f"Error initializing camera: {e}")
    return None  # Return None to indicate failure

def stop_camera(picam2):
  """Stop the camera."""
  if picam2:
    picam2.stop()
    print("Camera stopped successfully.")
