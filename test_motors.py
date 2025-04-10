import serial
import time

# Connect to Arduino (change port if needed)
arduino = serial.Serial(port='/dev/ttyACM0', baudrate=9600, timeout=1)
time.sleep(2)  # Wait for Arduino to initialize

def move_motor(command, degrees):
    message = f"{command}:{degrees}\n"
    arduino.write(message.encode())
    print(f"Sent: {message.strip()}")
    time.sleep(0.5)

def test_motor_steps(start, stop, step, command):
    print(f"\nTesting motor: {command}")
    degrees = start
    while degrees <= stop:
        move_motor(command, degrees)
        degrees += step
        time.sleep(1)

    print(f"Reversing...")
    degrees = stop
    while degrees >= start:
        move_motor(command, degrees)
        degrees -= step
        time.sleep(1)

if __name__ == "__main__":
    # Set the test parameters here
    start_angle = 0
    stop_angle = 5
    test_step = 0.1  # Try 0.1°, 0.5°, 1°, etc.

    # Test detector azimuthal and radial
    test_motor_steps(start_angle, stop_angle, test_step, "DET_AZ")
    test_motor_steps(start_angle, stop_angle, test_step, "DET_RAD")

    # Uncomment to test light motors if implemented
    # test_motor_steps(start_angle, stop_angle, test_step, "LIGHT_AZ")
    # test_motor_steps(start_angle, stop_angle, test_step, "LIGHT_RAD")

    print("Motor testing complete.")
