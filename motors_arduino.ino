// === Pin Definitions ===
// Make sure pins match your setup
#define DET_AZ_STEP 3
#define DET_AZ_DIR 2
#define DET_RAD_STEP 5
#define DET_RAD_DIR 4
#define LIGHT_AZ_STEP 7
#define LIGHT_AZ_DIR 6
#define LIGHT_RAD_STEP 9
#define LIGHT_RAD_DIR 8

// === Constants ===
// TODO: Change if necessary (how many steps the motor does per degree depends on the setup)
const float DET_AZ_STEPS_PER_DEG = 12.0;
const float DET_RAD_STEPS_PER_DEG = 10.0;
const float LIGHT_AZ_STEPS_PER_DEG = 12.0;
const float LIGHT_RAD_STEPS_PER_DEG = 10.0;
const unsigned int STEP_DELAY_US = 500;  // Motor speed control

// === State ===
long current_det_az_steps = long(8 * DET_AZ_STEPS_PER_DEG);
long current_det_rad_steps = long(8 * DET_RAD_STEPS_PER_DEG);
long current_light_az_steps = long(8 * LIGHT_AZ_STEPS_PER_DEG);
long current_light_rad_steps = long(8 * LIGHT_RAD_STEPS_PER_DEG);

// === Enum for Axis Selection ===
enum MotorAxis {
  DETECTOR_AZ,
  DETECTOR_RAD,
  LIGHT_AZ,
  LIGHT_RAD
};

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
  pinMode(LIGHT_AZ_STEP, OUTPUT);
  pinMode(LIGHT_AZ_DIR, OUTPUT);
  pinMode(LIGHT_RAD_STEP, OUTPUT);
  pinMode(LIGHT_RAD_DIR, OUTPUT);

  Serial.println("Motor controller ready.");
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();

    if (command == "RESET_POS") {
      reset_position();
      return;
    }

    int colonIndex = command.indexOf(':');
    if (colonIndex == -1) {
      Serial.println("Invalid format.");
      return;
    }

    String target = command.substring(0, colonIndex);
    float angle = command.substring(colonIndex + 1).toFloat();

    if (target == "DET_AZ_ABS") {
      move_to_absolute(DETECTOR_AZ, angle);
    } else if (target == "DET_RAD_ABS") {
      move_to_absolute(DETECTOR_RAD, angle);
    } else if (target == "LIGHT_AZ_ABS") {
      move_to_absolute(LIGHT_AZ, angle);
    } else if (target == "LIGHT_RAD_ABS") {
      move_to_absolute(LIGHT_RAD, angle);
    } else {
      Serial.println("Unknown command.");
    }
  }
}

void move_to_absolute(MotorAxis axis, float target_angle) {
  long target_steps = 0;
  long* current_steps;
  int step_pin, dir_pin;
  float steps_per_deg;

  switch (axis) {
    case DETECTOR_AZ:
      steps_per_deg = DET_AZ_STEPS_PER_DEG;
      current_steps = &current_det_az_steps;
      step_pin = DET_AZ_STEP;
      dir_pin = DET_AZ_DIR;
      break;
    case DETECTOR_RAD:
      steps_per_deg = DET_RAD_STEPS_PER_DEG;
      current_steps = &current_det_rad_steps;
      step_pin = DET_RAD_STEP;
      dir_pin = DET_RAD_DIR;
      break;
    case LIGHT_AZ:
      steps_per_deg = LIGHT_AZ_STEPS_PER_DEG;
      current_steps = &current_light_az_steps;
      step_pin = LIGHT_AZ_STEP;
      dir_pin = LIGHT_AZ_DIR;
      break;
    case LIGHT_RAD:
      steps_per_deg = LIGHT_RAD_STEPS_PER_DEG;
      current_steps = &current_light_rad_steps;
      step_pin = LIGHT_RAD_STEP;
      dir_pin = LIGHT_RAD_DIR;
      break;
  }

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

  *current_steps = target_steps;

  Serial.print("Moved ");
  switch (axis) {
    case DETECTOR_AZ: Serial.print("DET_AZ"); break;
    case DETECTOR_RAD: Serial.print("DET_RAD"); break;
    case LIGHT_AZ: Serial.print("LIGHT_AZ"); break;
    case LIGHT_RAD: Serial.print("LIGHT_RAD"); break;
  }
  Serial.print(" to ");
  Serial.print(target_angle, 2);
  Serial.println(" degrees.");
  Serial.println("OK");
}

void reset_position() {
  current_det_az_steps = long(8 * DET_AZ_STEPS_PER_DEG);
  current_det_rad_steps = long(8 * DET_RAD_STEPS_PER_DEG);
  current_light_az_steps = long(8 * LIGHT_AZ_STEPS_PER_DEG);
  current_light_rad_steps = long(8 * LIGHT_RAD_STEPS_PER_DEG);

  Serial.println("Position reset to 8 degrees on all axes.");
  Serial.println("OK");
}
