#Bringing it all together

import RPi.GPIO as GPIO
import time
import sys
import termios
import tty

selectBtnPin = 33
incBtnPin = 37
decBtnPin = 35
targetIndex = 0

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
	
# GPIO.setmode(GPIO.BOARD) !!! change btn pins above to be BCM number not board number !!

GPIO.setup(selectBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(incBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(decBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=select, bouncetime=200)
GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=inc_select, bouncetime=200)
GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=dec_select, bouncetime=200)

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

def select(channel):
	global targetIndex
	global planets
	global stepperPinsAZ
	global stepperPinsEL
	if GPIO.input(channel) == GPIO.LOW:
		eph = getPlanetInfo(planets[planetIndex])
		percentageArcAZ = (eph['AZ'][0])/360 #find Azimuth
		percentageArcEL = (eph['EL'][0])/360 #find Elevation
		stepsNeededAZ = int(percentageArcAZ*512) #512 steps is 360degrees
		stepsNeededEL = int(percentageArcEL*512) #512 steps is 360degrees

		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		lcd.crlf()
		lcd.write_string("AZ " + str(int(eph['AZ'][0])) + " EL " + str(int(eph['EL'][0])))
		time.sleep(1)
		print("ok button pressed")
		if stepsNeededAZ > 256:
			moveStepperBack(stepperPinsAZ, (512-stepsNeededAZ)) #rotates anticlockwise
		else:
			moveStepper(stepperPinsAZ, stepsNeededAZ) #rotates clockwise
		time.sleep(1)
		if stepsNeededEL < 0:
			moveStepperBack(stepperPinsEL, -stepsNeededEL) #rotates downwards
		else:
			moveStepper(stepperPinsEL, stepsNeededEL) #rotates upwards
		time.sleep(8)
		#moves back to starting position
		if stepsNeededEL < 0:
			moveStepper(stepperPinsEL, -stepsNeededEL)
		else:
			moveStepperBack(stepperPinsEL, stepsNeededEL)
		time.sleep(1)
		if stepsNeededAZ > 256:
			moveStepper(stepperPinsAZ, (512-stepsNeededAZ)) #rotates anticlockwise
		else:
			moveStepperBack(stepperPinsAZ, stepsNeededAZ) #rotates clockwise
		time.sleep(1)
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])


def inc_select(channel):
	global targetIndex
	if GPIO.input(channel) == GPIO.LOW:
		if targetIndex < 8:
			targetIndex = targetIndex + 1
		print("inc button pressed")
		time.sleep(1)

def dec_select(channel):
	global targetIndex
	if GPIO.input(channel) == GPIO.LOW:
		if targetIndex > 0:
			targetIndex = targetIndex - 1
		print("dec button pressed")
		time.sleep(1)

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