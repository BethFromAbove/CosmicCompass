# sudo apt install python3-pip
# pip3 install --pre --upgrade astroquery

# from astroquery.jplhorizons import Horizons

# from astroquery.simbad import Simbad

# # Query SIMBAD for the Andromeda Galaxy (M31)
# result_table = Simbad.query_object('M31')
# print(result_table)

# print(result_table.columns)
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

from astropy.coordinates import EarthLocation,SkyCoord
from astropy.time import Time
from astropy import units as u
from astropy.coordinates import AltAz

observing_location = EarthLocation(lat='51.2832', lon='0', height=100*u.m)  
observing_time = Time.now()  
aa = AltAz(location=observing_location, obstime=observing_time)

coord = SkyCoord('0h42m', '41d16m09.0s')
print(coord.transform_to(aa))


