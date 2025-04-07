import serial
import time

# Connect to Arduino
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)  # Update COM port as needed
time.sleep(2)  # Allow time to initialize

#def move_light_azimuthal(degrees):
 #   command = f"LIGHT_AZ:{degrees}\n"
  #  arduino.write(command.encode())

#def move_light_radial(degrees):
 #   command = f"LIGHT_RAD:{degrees}\n"
 #   arduino.write(command.encode())

def move_detector_azimuthal(degrees):
    command = f"DET_AZ:{degrees}\n"
    arduino.write(command.encode())

def move_detector_radial(degrees):
    command = f"DET_RAD:{degrees}\n"
    arduino.write(command.encode())
