import RPi.GPIO as GPIO
import time
import sys
import termios
import tty
import board
import neopixel
from astroquery.jplhorizons import Horizons
from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz

select_btn_pin = 26
inc_btn_pin = 6
dec_btn_pin = 5
pixel_pin = board.D18

is_initiliased = False

steps_full_circle_az = 3200
steps_full_circle_el = 6400
current_az_el = [0, 0]
current_position = [0, 0]

mercury = {"name": "Mercury", "lookup_value": 199}
venus = {"name": "Venus", "lookup_value": 299}
moon = {"name": "Moon", "lookup_value": 301}
mars = {"name": "Mars", "lookup_value": 499}
jupiter = {"name": "Jupiter", "lookup_value": 599}
saturn = {"name": "Saturn", "lookup_value": 699}
uranus = {"name": "Uranus", "lookup_value": 799}
neptune = {"name": "Neptune", "lookup_value": 899}
pluto = {"name": "Pluto", "lookup_value": 999}
jwst = {"name": "jwst", "lookup_value": "jwst"}
voyager = {"name": "Voyager", "lookup_value": "voyager 1"}
andromeda = {"name": "Andromeda", "lookup_value": "m31"}

body_index = 11
num_pixels = 12
bodies = [mercury, venus, moon, mars, jupiter, saturn, uranus, neptune, pluto, jwst, voyager, andromeda]
pixel_location = [11, 10, 9, 8, 7, 3, 4, 5, 6, 2, 1, 0]

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
    
GPIO.setup(select_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(inc_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(dec_btn_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
        
def getPlanetInfo(planet):
    obj = Horizons(id=planet, location='000', epochs=None, id_type=None)
    eph = obj.ephemerides()
    return eph

def get_andromeda_info():
    # update location if needed (Bristol lat='51.453', lon='-2.573')
    observing_location = EarthLocation(lat='51.453', lon='-2.573', height=100*u.m)  
    observing_time = Time.now()  
    aa = AltAz(location=observing_location, obstime=observing_time)

    coord = SkyCoord('0h42m', '41d16m09.0s') # andromeda has a fixed ra and dec
    sky_coord_alt_az = coord.transform_to(aa)
    print(f"Altitude: {sky_coord_alt_az.alt.degree:.2f}°")
    print(f"Azimuth: {sky_coord_alt_az.az.degree:.2f}°")
    alt_az = [sky_coord_alt_az.alt.degree.item(), sky_coord_alt_az.az.degree.item()]
    return alt_az

def get_stepsAz_stepsEl():
    global body_index
    if bodies[body_index]["name"] == "Andromeda":
        alt_az = get_andromeda_info()        
    else:
        eph = getPlanetInfo(bodies[body_index]["lookup_value"])
        alt_az = [eph['AZ'][0], eph['EL'][0]]
    steps_needed_az = int((alt_az[0]/360)*steps_full_circle_az) #6400 steps is 360degrees
    steps_needed_el = int((alt_az[1]/360)*steps_full_circle_el) #6400 steps is 360degrees
    return [steps_needed_az, steps_needed_el]


def inc_select(channel):
    global body_index
    if GPIO.input(channel) == GPIO.HIGH:
        pixels[pixel_location[body_index]] = OFF
        if body_index < 11:
            body_index = body_index + 1
        else:
            body_index = 0
        print("inc button pressed")
        print(body_index)
        pixels[pixel_location[body_index]] = BLUE
        pixels.show()

def dec_select(channel):
    global body_index
    if GPIO.input(channel) == GPIO.HIGH:
        pixels[pixel_location[body_index]] = OFF
        if body_index > 0:
            body_index = body_index - 1
        else:
            body_index = 11
        print("dec button pressed")
        print(body_index)
        pixels[pixel_location[body_index]] = BLUE
        pixels.show()


def select(channel):
    # Ignore the first button press, it always triggers for some reason
    global is_initiliased
    if is_initiliased == False:
        is_initiliased = True
        print("Caught first press")
        return None

    global body_index
    global current_az_el
    if GPIO.input(channel) == GPIO.HIGH:
        print("select button pressed")

        # get planet info
        steps_az_el_from_0 = get_stepsAz_stepsEl() # steps from 0, 0

        # need to account for previous location
        steps_needed_az = steps_az_el_from_0[0] - current_az_el[0]
        steps_needed_el = steps_az_el_from_0[1] - current_az_el[1]

        print(f"steps needed az = {steps_needed_az}")
        print(f"steps needed el = {steps_needed_el}")

        # position wire at 180 degrees, dont let it cross 0 to maximise slack in wires
        # shouldn't happen anyway because we're using delta between positions but added just in case

        if (current_az_el[0] + steps_needed_az) > steps_full_circle_az:
            steps_needed_az = steps_needed_az - steps_full_circle_az
        elif (current_az_el[0] + steps_needed_az) < 0:
            steps_needed_az = steps_needed_az + steps_full_circle_az

        # need to move clockwise for positive delta and anyiclockwise for negative delta

        if steps_needed_az < 0:
            set_direction(MOTOR1, True) # Rotates anticlockwise
            step_motor(MOTOR1, -steps_needed_az)
        else:
            set_direction(MOTOR1, False) # Rotates clockwise
            step_motor(MOTOR1, steps_needed_az)
        time.sleep(1)
        if steps_needed_el < 0:
            set_direction(MOTOR2, False) # Rotates downwards
            step_motor(MOTOR2, -steps_needed_el)
        else:
            set_direction(MOTOR2, True) # Rotates upwards
            step_motor(MOTOR2, steps_needed_el)
        
        # update current position
        current_az_el = [steps_az_el_from_0[0], steps_az_el_from_0[1]]
        print(f"current az el = {current_az_el}")

        time.sleep(2)
        
        # old code
        # if steps_needed_az > (steps_full_circle/2):
        #     set_direction(MOTOR1, True) # Rotates anticlockwise
        #     step_motor(MOTOR1, steps_full_circle-steps_needed_az)
        # else:
        #     set_direction(MOTOR1, False) # Rotates clockwise
        #     step_motor(MOTOR1, steps_needed_az)
        # time.sleep(1)
        # if steps_needed_el < 0:
        #     set_direction(MOTOR2, False) # Rotates downwards
        #     step_motor(MOTOR2, -steps_needed_el) #steps_needed_el is negative
        # else:
        #     set_direction(MOTOR2, True) # Rotates upwards
        #     step_motor(MOTOR2, steps_needed_el)
           
        
# Start up functions

def increaseAZ(channel):
    print("increaseAZ")
    if GPIO.input(channel) == GPIO.LOW:
        print("if statement az")
        set_direction(MOTOR1, True)
        step_motor(MOTOR1, 100)

def decreaseAZ(channel):
    print("decreaseAZ")
    if GPIO.input(channel) == GPIO.LOW:
        print("decrease az if statement")
        set_direction(MOTOR1, False)
        step_motor(MOTOR1, 100)

def increaseEL(channel):
    print("increaseEL")
    if GPIO.input(channel) == GPIO.LOW:
        print("increase el if statement")
        set_direction(MOTOR2, True)
        step_motor(MOTOR2, 100)
          
def decreaseEL(channel):
    print("decrese el")
    if GPIO.input(channel) == GPIO.LOW:
        print("decrease el if ststement")
        set_direction(MOTOR2, False)
        step_motor(MOTOR2, 100)
        
def clearNeopixels():
	for location in pixel_location:
		pixels[location] = OFF
	pixels.show()
          
# Set Altitude
def startUp():
    print("adjust vertical")
    clearNeopixels()
    pixels[pixel_location[2]] = GREEN
    pixels[pixel_location[10]] = GREEN
    pixels.show()
    GPIO.add_event_detect(select_btn_pin, GPIO.FALLING, callback=startUpNext, bouncetime=200)
    GPIO.add_event_detect(inc_btn_pin, GPIO.FALLING, callback=increaseEL, bouncetime=200)
    GPIO.add_event_detect(dec_btn_pin, GPIO.FALLING, callback=decreaseEL, bouncetime=200)
    time.sleep(1)

# Set Azimuth
def startUpNext(channel):
    if GPIO.input(channel) == GPIO.LOW:
        print("adjust azimuth")
        clearNeopixels()
        pixels[pixel_location[5]] = GREEN
        pixels[pixel_location[8]] = GREEN
        pixels.show()
        GPIO.remove_event_detect(select_btn_pin)
        GPIO.remove_event_detect(inc_btn_pin)
        GPIO.remove_event_detect(dec_btn_pin)
        GPIO.add_event_detect(select_btn_pin, GPIO.FALLING, callback=startUpFinish, bouncetime=200)
        GPIO.add_event_detect(inc_btn_pin, GPIO.FALLING, callback=increaseAZ, bouncetime=200)
        GPIO.add_event_detect(dec_btn_pin, GPIO.FALLING, callback=decreaseAZ, bouncetime=200)
        time.sleep(1)

def startUpFinish(channel):
    if GPIO.input(channel) == GPIO.LOW:
        GPIO.remove_event_detect(select_btn_pin)
        GPIO.remove_event_detect(inc_btn_pin)
        GPIO.remove_event_detect(dec_btn_pin)
        GPIO.add_event_detect(select_btn_pin, GPIO.FALLING, callback=select, bouncetime=500)#Setup event on falling edge
        GPIO.add_event_detect(inc_btn_pin, GPIO.FALLING, callback=inc_select, bouncetime=500)
        GPIO.add_event_detect(dec_btn_pin, GPIO.FALLING, callback=dec_select, bouncetime=500)
        clearNeopixels()
        pixels[pixel_location[body_index]] = WHITE
        pixels.show()
        #is_initiliased = True
        print("start up finished")
        time.sleep(3)
        

startUp()

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
            step_motor(MOTOR1, 500)

        elif key == 'a':
            set_direction(MOTOR1, False)
            step_motor(MOTOR1, 500)

        elif key == 'w':
            set_direction(MOTOR2, True)
            step_motor(MOTOR2, 500) #6400 is a full circle

        elif key == 's':
            set_direction(MOTOR2, False)
            step_motor(MOTOR2, 500)

        elif key == 'x':
            break

finally:
    GPIO.cleanup()
    print("GPIO cleaned up")
