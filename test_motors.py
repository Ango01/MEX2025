import serial
import time

# === Settings ===
SERIAL_PORT = '/dev/ttyACM0'   # Change this to match your Arduino port
BAUDRATE = 9600
STEP_DELAY = 0.5  # seconds between movements

# === Initialize Serial ===
arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Give Arduino time to reset

def send_motor_command(axis, steps):
    """
    Send a motor command to the Arduino.
    axis: 'AZ' or 'RAD'
    steps: positive (forward) or negative (backward) integer
    """
    command = f"DET:{axis}:{steps}\n"
    arduino.write(command.encode())
    print(f"Sent: {command.strip()}")

    # Wait for Arduino response
    while True:
        response = arduino.readline().decode().strip()
        if response:
            print(f"Arduino: {response}")
            break

def test_motor(axis, max_steps, step_size):
    """
    Move motor forward and backward to test precision.
    """
    print(f"\nTesting DETECTOR {axis} motor...")

    # Forward movement
    for steps in range(step_size, max_steps + 1, step_size):
        send_motor_command(axis, steps)
        time.sleep(STEP_DELAY)

    # Backward movement
    for steps in range(max_steps, 0, -step_size):
        send_motor_command(axis, -steps)
        time.sleep(STEP_DELAY)

    print(f"{axis} test complete.\n")

if __name__ == "__main__":
    try:
        # Test azimuthal motor
        test_motor(axis="AZ", max_steps=300, step_size=100)

        # Test radial motor
        test_motor(axis="RAD", max_steps=200, step_size=50)

    except KeyboardInterrupt:
        print("Test interrupted.")
    finally:
        arduino.close()
        print("Serial connection closed.")
