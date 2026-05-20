# sudo apt install python3-pip
# pip3 install --pre --upgrade astroquery

from astroquery.jplhorizons import Horizons
jamesWebb = Horizons(id='jwst', location = '000', epochs=None, id_type=None)
eph = jamesWebb.ephemerides()
print(eph)

print(eph['AZ'][0])
print(eph['EL'][0])

percentageArcAZ = (eph['AZ'][0])/360 #find Azimuth
percentageArcEL = (eph['EL'][0])/360 #find Elevation

print(percentageArcAZ)
print(percentageArcEL)

stepsNeededAZ = int(percentageArcAZ*512) #512 steps is 360degrees
stepsNeededEL = int(percentageArcEL*512) #512 steps is 360degrees

print(stepsNeededAZ)
print(stepsNeededEL)
