import serial
import time

# === Configuration ===
SERIAL_PORT = '/dev/ttyACM0'   # Update if needed
BAUDRATE = 9600
WAIT_TIME = 2.0                # Wait after each move (seconds)

# === Connect to Arduino ===
arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Allow Arduino time to reset

# === Read initial startup lines from Arduino ===
while arduino.in_waiting:
    print(arduino.readline().decode().strip())

def send_command(command):
    """Send command and print Arduino response."""
    arduino.write(f"{command}\n".encode())
    print(f"Sent: {command}")
    
    while True:
        response = arduino.readline().decode().strip()
        if response:
            print(f"Arduino: {response}")
            break

def test_motor(axis_name, command_prefix, start=0, stop=90, step=10):
    """
    Move a motor through a range of angles and record response.
    Use this to estimate degrees per step by observing actual movement.
    """
    print(f"\n--- Testing {axis_name} Motor ---")
    for angle in range(start, stop + 1, step):
        cmd = f"{command_prefix}:{angle:.2f}"
        send_command(cmd)
        print(f"Moved to {angle:.2f}° — record actual angle manually.")
        input("Press Enter to continue to next step...\n")
        time.sleep(WAIT_TIME)

    print(f"\n{axis_name} Test Complete.\n")

# === MAIN TEST SEQUENCE ===
if __name__ == "__main__":
    try:
        print("Starting motor test. Ensure system is safe.")
        test_motor("Detector AZIMUTH", "DET_AZ_ABS")
        test_motor("Detector RADIAL", "DET_RAD_ABS")
        test_motor("Light AZIMUTH", "LIGHT_AZ_ABS")
        test_motor("Light RADIAL", "LIGHT_RAD_ABS")
    except KeyboardInterrupt:
        print("Test interrupted by user.")
    finally:
        arduino.close()
        print("Serial connection closed.")


