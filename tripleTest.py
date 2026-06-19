# Testing neopixels, buttons and stepper motors together

import RPi.GPIO as GPIO
import time
import sys
import termios
import tty
import neopixel

selectBtnPin = 26
incBtnPin = 5
decBtnPin = 6
pixel_pin = 18

num_pixels = 8
targetIndex = 0
#planets = [199, 299, 301, 499, 599, 699, 799, 899, 999]
#bodies = ['Mercury', 'Venus', 'Moon', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'jwst', 'voyager 1', 'andromeda']

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
    
GPIO.setup(selectBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(incBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(decBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
)

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
OFF = (0, 0, 0)

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
        
# def getPlanetInfo(planet):
#     obj = Horizons(id=planet, location='000', epochs=None, id_type=None)
#     eph = obj.ephemerides()
#     return eph

def inc_select(channel):
    global targetIndex
    if GPIO.input(channel) == GPIO.LOW:
        pixels[targetIndex] = OFF
        if targetIndex < 11:
            targetIndex = targetIndex + 1
        else:
            targetIndex = 0
        print("inc button pressed")
        pixels[targetIndex] = WHITE
        pixels.show()
        time.sleep(0.5)

def dec_select(channel):
    global targetIndex
    if GPIO.input(channel) == GPIO.LOW:
        pixels[targetIndex] = OFF
        if targetIndex > 0:
            targetIndex = targetIndex - 1
        else:
            targetIndex = 11
        print("dec button pressed")
        pixels[targetIndex] = WHITE
        pixels.show()
        time.sleep(0.5)

def select(channel):
    global targetIndex
    if GPIO.input(channel) == GPIO.LOW:
        print("ok button pressed")

        set_direction(MOTOR1, True)
        step_motor(MOTOR1, 20)
        
        time.sleep(2)
        set_direction(MOTOR2, True)
        step_motor(MOTOR2, 20)

        time.sleep(2)
        set_direction(MOTOR1, False)
        step_motor(MOTOR1, 20)
        
        time.sleep(2)
        set_direction(MOTOR2, False)
        step_motor(MOTOR2, 20)
        
        
        
GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=select, bouncetime=200)
GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=inc_select, bouncetime=200)
GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=dec_select, bouncetime=200)


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
            step_motor(MOTOR1, 20)

        elif key == 'a':
            set_direction(MOTOR1, False)
            step_motor(MOTOR1, 20)

        elif key == 'w':
            set_direction(MOTOR2, True)
            step_motor(MOTOR2, 20)

        elif key == 's':
            set_direction(MOTOR2, False)
            step_motor(MOTOR2, 20)

        elif key == 'x':
            break

finally:
    GPIO.cleanup()
    print("GPIO cleaned up")