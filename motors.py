import serial
import time

# Connect to Arduino
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)  # Update COM port as needed
time.sleep(2)  # Allow time to initialize

LIGHT_AZ_STEPS_PER_DEG = 10
LIGHT_RAD_STEPS_PER_DEG = 8
DETECTOR_AZ_STEPS_PER_DEG = 12
DETECTOR_RAD_STEPS_PER_DEG = 10

class Motors:
    def __init__(self):
        self.light_az_offset = 0
        self.light_rad_offset = 0
        self.detector_az_offset = 0
        self.detector_rad_offset = 0

    def move_light_to_offset(self):
        self.move_light_azimuthal(self.light_az_offset)
        self.move_light_radial(self.light_rad_offset)

    def move_detector_to_offset(self):
        self.move_detector_azimuthal(self.detector_az_offset)
        self.move_detector_radial(self.detector_rad_offset)

    def move_light_azimuthal(self, angle):
        steps = int(angle * LIGHT_AZ_STEPS_PER_DEG)
        print(f"Rotating light azimuthal to {angle}° -> {steps} steps")
        command = f"LIGHT_AZ:{steps}\n"
        arduino.write(command.encode())
        time.sleep(0.1)

    def move_light_radial(self, angle):
        steps = int(angle * LIGHT_RAD_STEPS_PER_DEG)
        print(f"Rotating light radial to {angle}° -> {steps} steps")
        command = f"LIGHT_RAD:{steps}\n"
        arduino.write(command.encode())
        time.sleep(0.1)

    def move_detector_azimuthal(self, angle):
        steps = int(angle * DETECTOR_AZ_STEPS_PER_DEG)
        print(f"Rotating detector azimuthal to {angle}° -> {steps} steps")
        command = f"DET_AZ:{steps}\n"
        arduino.write(command.encode())
        time.sleep(0.1)

    def move_detector_radial(self, angle):
        steps = int(angle * DETECTOR_RAD_STEPS_PER_DEG)
        print(f"Rotating detector radial to {angle}° -> {steps} steps")
        command = f"DET_RAD:{steps}\n"
        arduino.write(command.encode())
        time.sleep(0.1)
