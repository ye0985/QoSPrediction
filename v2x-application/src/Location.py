from pynmeagps import NMEAReader
import settings
import subprocess
import re
import random
import s2sphere
import pydantic




def get_lat(nmea):
    pattern = r'\$GPGGA.*'
    gpgga = ""
    for gps in nmea:
        if re.match(pattern, gps):
            gpgga = gps
            break
    if gpgga == "":
        raise GPSError("GPGGA Format not found in nmea")
    return NMEAReader.parse(gpgga).lat


def get_lon(nmea):
    pattern = r'\$GPGGA.*'
    gpgga = ""
    for gps in nmea:
        if re.match(pattern, gps):
            gpgga = gps
            break
    if gpgga == "":
        raise GPSError("GPGGA Format not found in nmea")
    return NMEAReader.parse(gpgga).lon

class GPSError(Exception):
    pass


def get_s2(nmea:str):
    lat = get_lat(nmea)
    lon = get_lon(nmea)
    point = s2sphere.LatLng.from_degrees(lat, lon)
    cell_id = s2sphere.CellId.from_lat_lng(point)
    #print(type(cell_id.id()))
    return cell_id.id()


class GPSLocation:


    def __init__(self,lat,lon):
        self.lat = lat
        self.lot = lon

class LocationWithCellId(pydantic.BaseModel):
    lat: float
    lon: float
    cellId: int