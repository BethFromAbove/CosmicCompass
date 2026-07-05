# sudo apt install python3-pip
# pip3 install --pre --upgrade astroquery


from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz


observing_location = EarthLocation(lat='51.453', lon='-2.573', height=100*u.m)  
observing_time = Time.now()  
aa = AltAz(location=observing_location, obstime=observing_time)

coord = SkyCoord('0h42m44.3s', '41d16m07.0s') # andromeda has a fixed ra and dec
alt_az = coord.transform_to(aa)
print(alt_az)


print(f"Altitude: {alt_az.alt.degree:.2f}°")
print(f"Azimuth: {alt_az.az.degree:.2f}°")

together = [alt_az.alt.degree.item(), alt_az.az.degree.item()]
print(together)



# body = Horizons(id='m31', location = '000', epochs=None, id_type=None)
# eph = body.ephemerides()
# print(eph)

# # jwst, 

# print(eph['AZ'][0])
# print(eph['EL'][0])

# percentageArcAZ = (eph['AZ'][0])/360 #find Azimuth
# percentageArcEL = (eph['EL'][0])/360 #find Elevation

# print(percentageArcAZ)
# print(percentageArcEL)

# stepsNeededAZ = int(percentageArcAZ*512) #512 steps is 360degrees
# stepsNeededEL = int(percentageArcEL*512) #512 steps is 360degrees

# print(stepsNeededAZ)
# print(stepsNeededEL)from astropy.coordinates import EarthLocation,SkyCoord




