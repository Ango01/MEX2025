// === Pin Definitions ===
#define DET_AZ_STEP 3
#define DET_AZ_DIR 2
#define DET_RAD_STEP 5
#define DET_RAD_DIR 4

// === Constants ===
const float DET_AZ_STEPS_PER_DEG = 12.0;
const float DET_RAD_STEPS_PER_DEG = 10.0;
const unsigned int STEP_DELAY_US = 500;  // Microseconds between step pulses (controls motor speed)

// === State ===
// Track current position in steps
long current_az_steps = long(8 * DET_AZ_STEPS_PER_DEG);
long current_rad_steps = long(8 * DET_RAD_STEPS_PER_DEG);

// === Enum for Axis Selection ===
enum MotorAxis { DETECTOR_AZ, DETECTOR_RAD };

// === Function Prototypes ===
void move_to_absolute(MotorAxis axis, float target_angle);
void move_motor(int step_pin, int dir_pin, int steps, bool direction);
void reset_position();

void setup() {
  Serial.begin(9600);

  pinMode(DET_AZ_STEP, OUTPUT);
  pinMode(DET_AZ_DIR, OUTPUT);
  pinMode(DET_RAD_STEP, OUTPUT);
  pinMode(DET_RAD_DIR, OUTPUT);

  Serial.println("Detector motor controller (absolute mode) ready.");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "RESET_POS") {
      reset_position();
      return;
    }

    // Expected: DET_AZ_ABS:30.0 or DET_RAD_ABS:120.0
    int colonIndex = command.indexOf(':');
    if (colonIndex == -1) {
      Serial.println("Invalid format.");
      return;
    }

    // Split command into motor target and angle
    String target = command.substring(0, colonIndex);
    float angle = command.substring(colonIndex + 1).toFloat();

    if (target == "DET_AZ_ABS") {
      move_to_absolute(DETECTOR_AZ, angle);
    } else if (target == "DET_RAD_ABS") {
      move_to_absolute(DETECTOR_RAD, angle);
    } else {
      Serial.println("Unknown command.");
    }
  }
}

void move_to_absolute(MotorAxis axis, float target_angle) {
  long target_steps = 0;   // Final desired step count
  long* current_steps;     // Pointer to current step count
  int step_pin, dir_pin;
  float steps_per_deg;

  if (axis == DETECTOR_AZ) {
    steps_per_deg = DET_AZ_STEPS_PER_DEG;
    current_steps = &current_az_steps;
    step_pin = DET_AZ_STEP;
    dir_pin = DET_AZ_DIR;
  } else {
    steps_per_deg = DET_RAD_STEPS_PER_DEG;
    current_steps = &current_rad_steps;
    step_pin = DET_RAD_STEP;
    dir_pin = DET_RAD_DIR;
  }

  // Convert target angle to steps
  target_steps = long(target_angle * steps_per_deg);
  long step_diff = target_steps - *current_steps;
  bool direction = step_diff >= 0;
  long move_steps = abs(step_diff);

  digitalWrite(dir_pin, direction ? HIGH : LOW);
  for (long i = 0; i < move_steps; i++) {
    digitalWrite(step_pin, HIGH);
    delayMicroseconds(STEP_DELAY_US);
    digitalWrite(step_pin, LOW);
    delayMicroseconds(STEP_DELAY_US);
  }

  // Update current position
  *current_steps = target_steps;

  Serial.print("Moved ");
  Serial.print((axis == DETECTOR_AZ) ? "AZ" : "RAD");
  Serial.print(" to ");
  Serial.print(target_angle, 2);
  Serial.println(" degrees.");

  Serial.println("OK");
}

// === Reset motor position counters to offset ===
void reset_position() {
  current_az_steps = long(8 * DET_AZ_STEPS_PER_DEG);
  current_rad_steps = long(8 * DET_RAD_STEPS_PER_DEG);

  Serial.println("Position reset to 8 degrees on both axes.");
  Serial.println("OK");
}
