import serial
import time

# === Configuration ===
SERIAL_PORT = '/dev/ttyACM0'   # Port where Arduino is connected
BAUDRATE = 9600                # Speed at which data is transmitted over serial connection
STEPS_PER_DEGREE = 10          # (motor_steps_per_rev * microstepping * gear_ratio) / 360 = (200 * 16 * gear_ratio) / 360
STEP_DELAY = 5                 # Time between moves (seconds)

# === Connect to Arduino ===
arduino = serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1)
time.sleep(2)  # Allow Arduino to reset

while arduino.in_waiting:
    line = arduino.readline().decode().strip()
    if line:
        print(f"(Arduino startup): {line}")

def send_motor_command(axis, steps):
    """Send command like DET:AZ:20 or DET:RAD:-15"""
    command = f"DET:{axis}:{steps}\n"
    arduino.write(command.encode())
    print(f"Sent: {command.strip()}")

    # Read and print Arduino response
    while True:
        response = arduino.readline().decode().strip()
        if response:
            print(f"Arduino: {response}")
            break

def move_detector_by_angle(az_angle, rad_angle):
    """Convert angles to steps and send commands to Arduino"""
    az_steps = round(az_angle * STEPS_PER_DEGREE)
    rad_steps = round(rad_angle * STEPS_PER_DEGREE)

    print(f"\nMoving AZ by {az_angle}° → {az_steps} steps")
    send_motor_command("AZ", az_steps)
    time.sleep(STEP_DELAY)

    print(f"Moving RAD by {rad_angle}° → {rad_steps} steps")
    send_motor_command("RAD", rad_steps)
    time.sleep(STEP_DELAY)

def run_angle_test():
    """Try different angle increments for both motors"""
    test_angles_az = [90, 90, 50, 90]    
    test_angles_rad = [90, 90, 90, 50]   

    print("Starting angle test...")

    for az_angle, rad_angle in zip(test_angles_az, test_angles_rad):
        move_detector_by_angle(az_angle, rad_angle)
    
    print("\nTest complete.")

if __name__ == "__main__":
    try:
        run_angle_test()
    except KeyboardInterrupt:
        print("Interrupted.")
    finally:
        arduino.close()
        print("Serial connection closed.")

