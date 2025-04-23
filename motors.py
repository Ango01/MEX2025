import serial
import time

class Motors:
    def __init__(self):
        # Connect to Arduino
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)  
        time.sleep(2)  # Allow time to initialize

        self.LIGHT_AZ_STEPS_PER_DEG = 10
        self.LIGHT_RAD_STEPS_PER_DEG = 8
        self.DETECTOR_AZ_STEPS_PER_DEG = 12
        self.DETECTOR_RAD_STEPS_PER_DEG = 10

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
        steps = int(angle * self.LIGHT_AZ_STEPS_PER_DEG)
        print(f"Rotating light azimuthal to {angle}° -> {steps} steps")
        command = f"LIGHT_AZ:{steps}\n"
        self.arduino.write(command.encode())
        time.sleep(5)

    def move_light_radial(self, angle):
        steps = int(angle * self.LIGHT_RAD_STEPS_PER_DEG)
        print(f"Rotating light radial to {angle}° -> {steps} steps")
        command = f"LIGHT_RAD:{steps}\n"
        self.arduino.write(command.encode())
        time.sleep(5)

    def move_detector_azimuthal(self, angle):
        steps = int(angle * self.DETECTOR_AZ_STEPS_PER_DEG)
        print(f"Rotating detector azimuthal to {angle}° -> {steps} steps")
        command = f"DET:AZ:{steps}\n"
        self.arduino.write(command.encode())
        time.sleep(5)

    def move_detector_radial(self, angle):
        steps = int(angle * self.DETECTOR_RAD_STEPS_PER_DEG)
        print(f"Rotating detector radial to {angle}° -> {steps} steps")
        command = f"DET:RAD:{steps}\n"
        self.arduino.write(command.encode())
        time.sleep(5)

