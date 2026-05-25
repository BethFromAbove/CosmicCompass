import time
import RPi.GPIO as GPIO

selectBtnPin = 37
# incBtnPin = 37
# decBtnPin = 35
# targetIndex = 0

def select(channel):
    print("button pressed")

# def select(channel):
# 	global targetIndex
# 	global planets
# 	global stepperPinsAZ
# 	global stepperPinsEL
# 	if GPIO.input(channel) == GPIO.LOW:
# 		eph = getPlanetInfo(planets[planetIndex])
# 		percentageArcAZ = (eph['AZ'][0])/360 #find Azimuth
# 		percentageArcEL = (eph['EL'][0])/360 #find Elevation
# 		stepsNeededAZ = int(percentageArcAZ*512) #512 steps is 360degrees
# 		stepsNeededEL = int(percentageArcEL*512) #512 steps is 360degrees

# 		lcd.clear()
# 		lcd.write_string(planetNames[planetIndex])
# 		lcd.crlf()
# 		lcd.write_string("AZ " + str(int(eph['AZ'][0])) + " EL " + str(int(eph['EL'][0])))
# 		time.sleep(1)
# 		print("ok button pressed")
# 		if stepsNeededAZ > 256:
# 			moveStepperBack(stepperPinsAZ, (512-stepsNeededAZ)) #rotates anticlockwise
# 		else:
# 			moveStepper(stepperPinsAZ, stepsNeededAZ) #rotates clockwise
# 		time.sleep(1)
# 		if stepsNeededEL < 0:
# 			moveStepperBack(stepperPinsEL, -stepsNeededEL) #rotates downwards
# 		else:
# 			moveStepper(stepperPinsEL, stepsNeededEL) #rotates upwards
# 		time.sleep(8)
# 		#moves back to starting position
# 		if stepsNeededEL < 0:
# 			moveStepper(stepperPinsEL, -stepsNeededEL)
# 		else:
# 			moveStepperBack(stepperPinsEL, stepsNeededEL)
# 		time.sleep(1)
# 		if stepsNeededAZ > 256:
# 			moveStepper(stepperPinsAZ, (512-stepsNeededAZ)) #rotates anticlockwise
# 		else:
# 			moveStepperBack(stepperPinsAZ, stepsNeededAZ) #rotates clockwise
# 		time.sleep(1)
# 		lcd.clear()
# 		lcd.write_string(planetNames[planetIndex])


# def inc_select(channel):
# 	global targetIndex
# 	if GPIO.input(channel) == GPIO.LOW:
# 		if targetIndex < 8:
# 			targetIndex = targetIndex + 1
# 		print("inc button pressed")
# 		time.sleep(1)

# def dec_select(channel):
# 	global targetIndex
# 	if GPIO.input(channel) == GPIO.LOW:
# 		if targetIndex > 0:
# 			targetIndex = targetIndex - 1
# 		print("dec button pressed")
# 		time.sleep(1)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(selectBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(incBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#GPIO.setup(decBtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.add_event_detect(selectBtnPin, GPIO.FALLING, callback=select, bouncetime=200)
#GPIO.add_event_detect(incBtnPin, GPIO.FALLING, callback=inc_select, bouncetime=200)
#GPIO.add_event_detect(decBtnPin, GPIO.FALLING, callback=dec_select, bouncetime=200)