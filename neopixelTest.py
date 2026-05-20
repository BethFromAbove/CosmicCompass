# sudo apt update
# sudo apt install python3-pip
# pip3 install rpi_ws281x adafruit-circuitpython-neopixel
# pip3 install --force-reinstall adafruit-blinka

import time
import board
import neopixel

# Choose the GPIO pin you connected your data line to (e.g., board.D18)
pixel_pin = board.D18

# Define the number of NeoPixels you have connected
num_pixels = 8

# Create the NeoPixel object
pixels = neopixel.NeoPixel(
    pixel_pin, num_pixels, brightness=0.2, auto_write=False, pixel_order=neopixel.GRB
)

# Define some basic colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OFF = (0, 0, 0)

# Run a test loop
def color_wipe(color, wait):
    pixels.fill(color)
    pixels.show()
    time.sleep(wait)

while True:
    color_wipe(RED, 0.5)
    color_wipe(GREEN, 0.5)
    color_wipe(BLUE, 0.5)
    color_wipe(OFF, 0.5)
