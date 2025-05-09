import serial
import time
import logging

# Control stepper motors via Arduino over serial connection
class Motors:
    def __init__(self):
        # Connect to Arduino
        self.arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)  
        time.sleep(2)  # Allow time to initialize

        # Default offset positions in degress
        self.light_az_offset = 8
        self.light_rad_offset = 8
        self.detector_az_offset = 8
        self.detector_rad_offset = 8

    def reset_position(self):
        """Assume that the position where the motors are at the moment is the starting point."""
        self.arduino.write(b"RESET_POS\n")
        response = self.arduino.readline().decode().strip()
        logging.info("Arduino response:", response)

    def home_detector_axes(self):
        """Rough homing by moving detector axes slowly toward a mechanical stop."""
        logging.info("Homing detector axes...")

        # Move far in negative direction to hit mechanical stop (assumes safe)
        for _ in range(100):  # Enough steps to reach stop
            self.arduino.write(b"DET_AZ_ABS:0\n")
            time.sleep(0.2)
        for _ in range(100):
            self.arduino.write(b"DET_RAD_ABS:0\n")
            time.sleep(0.2)

        logging.info("Homing move complete. Setting current position to 8° offset.")
        self.reset_position()

    def move_light_to_offset(self):
        """Move light source axes (azimuthal and radial) to offset position."""
        self.move_light_azimuthal(self.light_az_offset)
        self.move_light_radial(self.light_rad_offset)

    def move_detector_to_offset(self):
        """Move detector axes (azimuthal and radial) to offset position."""
        self.move_detector_azimuthal(self.detector_az_offset)
        self.move_detector_radial(self.detector_rad_offset)

    def move_light_azimuthal(self, angle):
        """Move light source in the azimuthal direction."""
        logging.info(f"Command: Go to light azimuthal {angle}°")
        command = f"LIGHT_AZ_ABS:{angle:.2f}\n"
        self.arduino.write(command.encode())
        response = self.arduino.readline().decode().strip()
        logging.info("Arduino response:", response)
        time.sleep(2)

    def move_light_radial(self, angle):
        """Move light source in the radial direction."""
        logging.info(f"Go to light radial {angle}°")
        command = f"LIGHT_RAD_ABS:{angle:.2f}\n"
        self.arduino.write(command.encode())
        response = self.arduino.readline().decode().strip()
        logging.info("Arduino response:", response)
        time.sleep(2)

    def move_detector_azimuthal(self, angle):
        """Move detector in the azimuthal direction."""
        logging.info(f"Go to detector azimuthal {angle}°")
        command = f"DET_AZ_ABS:{angle:.2f}\n"
        self.arduino.write(command.encode())
        response = self.arduino.readline().decode().strip()
        logging.info("Arduino response:", response)
        time.sleep(2)

    def move_detector_radial(self, angle):
        """Move detector in the radial direction."""
        logging.info(f"Go to detector radial {angle}°")
        command = f"DET_RAD_ABS:{angle:.2f}\n"
        self.arduino.write(command.encode())
        response = self.arduino.readline().decode().strip()
        logging.info("Arduino response:", response)
        time.sleep(2)

