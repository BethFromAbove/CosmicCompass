import RPi.GPIO as GPIO
import time
import sys
import termios
import tty

# ------------------------
# GPIO SETUP
# ------------------------

MOTOR1 = {"STEP": 17, "DIR": 27, "EN": 22}
MOTOR2 = {"STEP": 23, "DIR": 24, "EN": 25}

GPIO.setmode(GPIO.BCM)

for motor in (MOTOR1, MOTOR2):
    GPIO.setup(motor["STEP"], GPIO.OUT)
    GPIO.setup(motor["DIR"], GPIO.OUT)
    GPIO.setup(motor["EN"], GPIO.OUT)
    GPIO.output(motor["EN"], GPIO.LOW)  # Enable (LOW for most drivers)

# ------------------------
# HELPER FUNCTIONS
# ------------------------

def step_motor(motor, steps, delay=0.001):
    for _ in range(steps):
        GPIO.output(motor["STEP"], GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(motor["STEP"], GPIO.LOW)
        time.sleep(delay)

def set_direction(motor, direction):
    GPIO.output(motor["DIR"], GPIO.HIGH if direction else GPIO.LOW)

def get_key():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

# ------------------------
# MAIN LOOP
# ------------------------

print("""
Controls:
Motor 1:
  q = forward
  a = backward

Motor 2:
  w = forward
  s = backward

Other:
  x = exit
""")

try:
    while True:
        key = get_key()

        if key == 'q':
            set_direction(MOTOR1, True)
            step_motor(MOTOR1, 200)

        elif key == 'a':
            set_direction(MOTOR1, False)
            step_motor(MOTOR1, 200)

        elif key == 'w':
            set_direction(MOTOR2, True)
            step_motor(MOTOR2, 200)

        elif key == 's':
            set_direction(MOTOR2, False)
            step_motor(MOTOR2, 200)

        elif key == 'x':
            break

finally:
    GPIO.cleanup()
    print("GPIO cleaned up")