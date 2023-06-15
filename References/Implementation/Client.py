from datetime import datetime
from Measurement import Measurement
from Modem import DummyModem, Modem

#import pyodbc
import settings
import time
import json
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


class Client:
    def __init__(self, measure_rate=30, save_to_file=True, save_to_database=True, random_values=False):
        self.measure_rate = measure_rate
        self.save_to_file = save_to_file
        self.save_to_database = save_to_database
        self.random_values = random_values
        self.measurements = []
        self.cnxn = None
        self.client = None
        self.write_api = None

        self.eutra_operating_bands = {1 : 1950, 2 : 1900, 3 : 1740, 4 : 1730, 5 : 836, 6 : 835, 7 : 2535, 8 : 887, 9 : 1777, 10 : 1740, 11 : 1437, 12 : 707, 13 : 782, 14 : 793, 17 : 710, 18 : 822, 19 : 838, 20 : 847, 21 : 1456, 22 : 3450, 23 : 2010, 24 : 1643, 25 : 1880, 26 : 831, 27 : 815, 28 : 725, 33 : 1919, 34 : 2017, 35 : 1880, 36 : 1960, 37 : 1920, 38 : 2595, 39 : 1895, 40 : 2350, 41 : 2595, 42 : 3500, 43 : 3700, 44 : 753}

    def main_loop(self):
        if self.random_values:
            modem = DummyModem()
        else:
            modem = Modem()

        if self.save_to_database:
            #self.cnxn = self.db_connect()
            self.client = self.influx_connect()

        for i in range(2):
        #while True:
            measurement = modem.measure()

            if self.save_to_file:
                dt = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
                with open(f"samples/output_{dt}", "w") as f:
                    f.write(json.dumps(measurement.dict()))
                    # f.write(modem.get_extra_information())

            if self.save_to_database:
                self.influx_write([measurement])

            print(json.dumps(measurement.dict()))
            # print(modem.get_extra_information())

            time.sleep(self.measure_rate)

    def dlink_band_from_band_ind(self, freq_band_ind):
        """map freq_band_ind to average value from Table 5.5-1 3GPP 36.101"""
        avg_downlink_band = self.eutra_operating_bands[freq_band_ind]
        if avg_downlink_band == None:
            print("Incorrect frequency_band_ind value")
            avg_downlink_band = -9999
        return avg_downlink_band

    def db_connect(self):
        server = settings.server
        database = settings.database
        username = settings.username
        password = settings.password
        cnxn = pyodbc.connect("DRIVER={ODBC Driver 17 for SQL Server};SERVER="+server+";DATABASE="+database+";UID="+username+";PWD="+password)
        cnxn.setdecoding(pyodbc.SQL_CHAR, encoding='utf-8')
        cnxn.setdecoding(pyodbc.SQL_WCHAR, encoding='utf-8')
        cnxn.setencoding(encoding='utf-8')
        return cnxn

#INFLUX DB
    def influx_connect(self):
        url = settings.url
        token = settings.token
        org = settings.org
        bucket = settings.bucket
        client = influxdb_client.InfluxDBClient(url=url,token=token, org=org)
        return client
    
    def create_write_api(self):
        write_api = self.client.write_api(write_options=SYNCHRONOUS)
        return write_api
    def influx_write(self, measurments: list[Measurement]):
        print(self.client)
        
        if self.write_api == None:
            self.write_api = self.create_write_api()
            print(self.write_api)
        dt = datetime.now().strftime("%d_%m_%Y_%H:%M:%S")
        for m in measurments:
                point = (Point(f"TimeSeries")
                .tag("signalStrength",m.signalStrength)
                .tag("signalStrengthLTE", m. signalStrengthLTE)
                .tag("networkProvider" , m.networkProvider)
                .tag("cellId", m.cellId)
                .tag("dlink", self.dlink_band_from_band_ind(m.frequency))
                .field("lat", m.lat)
                .field("lon", m.lon))
                #print(m.gpsNmea["$GPGGA"])
                print(f"Lat:{m.lat} Lon:{m.lon}")
                self.write_api.write(bucket=settings.bucket, org=settings.org, record=point)
        

    def db_write(self, measurements: list[Measurement]):
        cursor = self.cnxn.cursor()
        for m in measurements:
            cursor.execute(f"INSERT INTO {settings.table_name} VALUES (?,?,?,?,?,?)", 
                m.signalStrength, m.signalStrengthLTE, m.networkProvider, m.cellId, self.dlink_band_from_band_ind(m.frequency), m.gpsNmea)
        self.cnxn.commit()

    def db_read(self) -> str:
        cursor = self.cnxn.cursor()
        cursor.execute("SELECT * FROM dbo.mobiledata")
        result = ""
        row = cursor.fetchone()
        while row:
            result += str(row) + "\n"
            row = cursor.fetchone()
        return result