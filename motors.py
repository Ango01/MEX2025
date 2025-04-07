import serial
import time

arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2) # Wait for Arduino to reset

# Send 'A' to move Motor 1
arduino.write(b'A')
time.sleep(1)

# Send 'B' to move Motor 2
arduino.write(b'B')