from RPLCD.gpio import CharLCD
import time
import RPi.GPIO as GPIO
from astroquery.jplhorizons import Horizons

inSetUp = True
planetIndex = 0
stepperPinsAZ = [7,11,13,15]
stepperPinsEL = [40, 38, 36, 32]
selectBtnPin = 33
incBtnPin = 37
decBtnPin = 35
mars = 499
planets = [199, 299, 301, 499, 599, 699, 799, 899, 999]
planetNames = ["Mercury", "Venus", "Moon", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]

def okSelect(channel):
	global planetIndex
	global planets
	global planetNames
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


def incSelect(channel):
	global planetIndex
	global planetNames
	if GPIO.input(channel) == GPIO.LOW:
		if planetIndex < 8:
			planetIndex = planetIndex + 1
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		print("inc button pressed")
		time.sleep(1)

def decSelect(channel):
	global planetIndex
	global planetNames
	if GPIO.input(channel) == GPIO.LOW:
		if planetIndex > 0:
			planetIndex = planetIndex - 1
		lcd.clear()
		lcd.write_string(planetNames[planetIndex])
		print("dec button pressed")
		time.sleep(1)

def startUp():
	lcd.clear()
	lcd.write_string("Setup Mode:")
	lcd.crlf()
	lcd.write_string("Adjust Vertical")
	GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=startUpNext, bouncetime=200)
	GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=increaseEL, bouncetime=200)
	GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=decreaseEL, bouncetime=200)
	time.sleep(1)

def increaseAZ(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepper(stepperPinsAZ, 32)

def decreaseAZ(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepperBack(stepperPinsAZ, 32)

def increaseEL(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepper(stepperPinsEL, 32)

def decreaseEL(channel):
	if GPIO.input(channel) == GPIO.LOW:
		moveStepperBack(stepperPinsEL, 32)

def startUpNext(channel):
	if GPIO.input(channel) == GPIO.LOW:
		lcd.clear
		lcd.write_string(" Setup Mode:")
		lcd.crlf()
		lcd.write_string("Adjust  Rotation")
		GPIO.remove_event_detect(selectBtnPin)
		GPIO.remove_event_detect(incBtnPin)
		GPIO.remove_event_detect(decBtnPin)
		GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=startUpFinish, bouncetime=200)
		GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=increaseAZ, bouncetime=200)
		GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=decreaseAZ, bouncetime=200)
		time.sleep(1)

def startUpFinish(channel):
	if GPIO.input(channel) == GPIO.LOW:
		global inSetUp
		GPIO.remove_event_detect(selectBtnPin)
		GPIO.remove_event_detect(incBtnPin)
		GPIO.remove_event_detect(decBtnPin)
		GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=okSelect, bouncetime=500)#Setup event on falling edge
		GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=incSelect, bouncetime=500)
		GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=decSelect, bouncetime=500)
		inSetUp = False
		time.sleep(1)

def getPlanetInfo(planet):
	obj = Horizons(id=planet, location='000', epochs=None, id_type='majorbody')
	eph = obj.ephemerides()
	return eph

def moveStepper(axis, stepsNeeded):
	halfstep_seq = [
		[1,0,0,0],
		[1,1,0,0],
		[0,1,0,0],
		[0,1,1,0],
		[0,0,1,0],
		[0,0,1,1],
		[0,0,0,1],
		[1,0,0,1]
	]
	for i in range(stepsNeeded):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(axis[pin], halfstep_seq[halfstep][pin])
			time.sleep(0.002)

def moveStepperBack(axis, stepsNeeded):
	halfstep_seq = [
		[1,0,0,1],
		[0,0,0,1],
		[0,0,1,1],
		[0,0,1,0],
		[0,1,1,0],
		[0,1,0,0],
		[1,1,0,0],
		[1,0,0,0]
	]
	for i in range(stepsNeeded):
		for halfstep in range(8):
			for pin in range(4):
				GPIO.output(axis[pin], halfstep_seq[halfstep][pin])
			time.sleep(0.002)


GPIO.setmode(GPIO.BOARD)

for pin in stepperPinsAZ + stepperPinsEL:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin,0)

lcd = CharLCD(cols=16, rows=2, dotsize=8, pin_rs=26,  pin_e=24, pins_data=[22, 18, 16, 12], numbering_mode=GPIO.BOARD)
lcd.clear()

GPIO.setup(selectBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(incBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(decBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

startUp()

while inSetUp:
	time.sleep(1)

lcd.clear()
lcd.write_string("Welcome to")
lcd.crlf()
lcd.write_string("Planet Finder")
time.sleep(2)

lcd.clear()
lcd.write_string("Select a planet")
lcd.crlf()
lcd.write_string("Mercury")
time.sleep(2)

while True:
	time.sleep(1)