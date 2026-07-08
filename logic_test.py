
import time
import sys

from astroquery.jplhorizons import Horizons
from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz


is_initiliased = False

steps_full_circle = 6400
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
bodies = [mercury, venus, moon, mars, jupiter, saturn, uranus, neptune, pluto, jwst, voyager, andromeda]
pixel_location = [11, 10, 9, 8, 7, 3, 4, 5, 6, 2, 1, 0]


# ------------------------
# HELPER FUNCTIONS
# ------------------------

        
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
        print(eph)
        alt_az = [eph['AZ'][0], eph['EL'][0]]
        print(alt_az)
    steps_needed_az = int((alt_az[0]/360)*steps_full_circle) #6400 steps is 360degrees
    steps_needed_el = int((alt_az[1]/360)*steps_full_circle) #6400 steps is 360degrees
    return [steps_needed_az, steps_needed_el]

def select():
    global body_index
    global current_az_el
    
    steps_az_steps_el = get_stepsAz_stepsEl() # steps from 0, 0

    print(f"steps_az_steps_el = {steps_az_steps_el}")

    # need to account for previous location
    steps_needed_az = steps_az_steps_el[0] - current_az_el[0]
    steps_needed_el = steps_az_steps_el[1] - current_az_el[1]

    print(f"steps needed az = {steps_needed_az}")
    print(f"steps needed el = {steps_needed_el}")

    print(f"steps needed az + current = {steps_needed_az + current_az_el[0]}")

    # position wire at 180 degrees

    # if current + steps > 360
    # then move steps -360
    # else if current +steps < 0 
    # then move steps + 360
    # else move steps


    if (current_az_el[0] + steps_needed_az) > 6400:
        steps_needed_az = steps_needed_az - 6400
        print(f"Too big. New steps needed az = {steps_needed_az}")
    elif (current_az_el[0] + steps_needed_az) < 0:
        steps_needed_az = steps_needed_az + 6400
        print(f"Too small. New steps needed az = {steps_needed_az}")
    else:
        print(f"No change needed")
    
    # update current position
    current_az_el = [steps_az_steps_el[0], steps_az_steps_el[1]]
    print(f"current az el = {current_az_el}")
    time.sleep(2)
        

# ------------------------
# MAIN LOOP
# ------------------------

print("""
Enter body index
""")

try:
    while True:
        x = input()
        body_index = int(x)
        select()

finally:
    print("end")
