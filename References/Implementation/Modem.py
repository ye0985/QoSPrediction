from importlib.util import resolve_name
import random
from Measurement import Measurement

import subprocess
import json
import serial
import time
import re

class Modem:

    #Constructor for Modem
    def __init__(self, modem_id=None, signal_update_rate=5):
        #get Modem ID
        self.modem_id = modem_id        
        if modem_id == None:
            self.modem_id = self.get_modem_id()
        #Enable the 5G Modem 
        command_signal_enable = ["mmcli", f"--modem={self.modem_id}", f"--enable"]
        self.run_command(command_signal_enable)
        command_signal_enable = ["mmcli", f"--modem={self.modem_id}", f"--signal-setup={signal_update_rate}", "-J"]
        self.run_command(command_signal_enable)
        command_location_enable = ["mmcli", f"--modem={self.modem_id}", "--location-enable-gps-nmea", "-J"]
        self.run_command(command_location_enable)
        time.sleep(1)


    def run_command(self, command):
        output = subprocess.run(command, capture_output=True)
        if len(output.stderr.decode()):
            print(f"Command {command} failed")
            print(output.stderr.decode())
            return ""
        return output.stdout.decode()

    def run_at_command(self, command):
        response = ""
        with serial.Serial("/dev/ttyUSB2", timeout=1, write_timeout=1, dsrdtr=True, rtscts=True) as ser:
            ser.reset_output_buffer()
            ser.write(b'' + command + b'\r')
            response = str(ser.read(size=1000).decode("utf-8"))
        return response

    def get_modem_id(self):
        """Return an ID of the first modem.
        Raise ModemError if no modem were found by ModemManager"""
        command_list_modems = ["mmcli", "-L", "-J"]
        modems_json = json.loads(self.run_command(command_list_modems))

        if not modems_json["modem-list"]:
            raise ModemError("No modem found")

        id = modems_json["modem-list"][0][-1]
        return int(id)

    def get_location_nmea(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--location-get"]
        location_json = json.loads(self.run_command(command))
        print(location_json)
        gps_nmea: str[list] = location_json["modem"]["location"]["gps"]["nmea"]
        gpsGPGGA = location_json["modem"]["location"]["gps"]["nmea"][5]
        return "\n".join(gps_nmea)

    def get_lat(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--location-get"]
        location_json = json.loads(self.run_command(command))
        gps_nmea: str[list] = location_json["modem"]["location"]["gps"]["nmea"]
        gpsGPGGA = location_json["modem"]["location"]["gps"]["nmea"][5]
        latitude = float(gpsGPGGA.split(',')[2])
        return latitude
    def get_lon(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--location-get"]
        location_json = json.loads(self.run_command(command))
        gps_nmea: str[list] = location_json["modem"]["location"]["gps"]["nmea"]
        gpsGPGGA = location_json["modem"]["location"]["gps"]["nmea"][5]
        latitude = float(gpsGPGGA.split(',')[4])
        return latitude
    def get_signal(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--signal-get"]
        signal_json = json.loads(self.run_command(command))
        rsrp: str = signal_json["modem"]["signal"]["5g"]["rsrp"][:-3]
        return int(rsrp)

    def get_signal_lte(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--signal-get"]
        signal_json = json.loads(self.run_command(command))
        rsrp: str = signal_json["modem"]["signal"]["lte"]["rsrp"][:-3]
        return int(rsrp)
        
    def get_provider(self):
        response = self.run_at_command(b"AT+COPS?")
        if "Telekom" in response:
            return "Telekom"
        elif "o2" in response:
            return "o2"
        elif "vodafone" in response:
            return "vodafone"
        else:
            return "provider unknown"

    def get_cellId(self):
        command = ["mmcli", f"--modem={self.modem_id}", "-J", "--location-get"]
        cellid_json = json.loads(self.run_command(command))
        cellid = cellid_json["modem"]["location"]["3gpp"]["cid"]
        print("CellID" + cellid)
        return int(cellid,16)
    
    def get_frequencyBand(self):
        response = self.run_at_command(b'AT+QENG="servingcell"')
        # no 5g signal
        if  not response.__contains__("NR5G-NSA"):
            return -9999
        # parse freq_band_ind from at command output
        freqBand = re.search(r"[\-0-9A-F]+,[\-0-9A-F]+,[\-0-9A-F]+,[\-0-9A-F]+,[\-0-9A-F]+,([0-9A-F]+),[\-0-9A-F]+,[\-0-9A-F]+,[\-0-9A-F]+", response)
        if freqBand == None:
            return -9999
        else:
            freqBand = freqBand.group(1)
        return int(freqBand)

    def measure(self) -> Measurement:
        m = Measurement(
            signalStrength=self.get_signal(),
            signalStrengthLTE=self.get_signal_lte(),
            networkProvider=self.get_provider(),
            cellId=self.get_cellId(),
            frequency=self.get_frequencyBand(),
            gpsNmea=self.get_location_nmea(),
            lat=self.get_lat(),
            #latC=
            lon=self.get_lon(),
            #lonC=
        )
        return m

    def get_extra_information(self):
        qops = 'AT+COPS?\n": ' + self.run_at_command(b'AT+COPS?')
        qeng = 'AT+QENG="servingcell\n": ' + self.run_at_command(b'AT+QENG="servingcell"')
        return qops + qeng

class DummyModem(Modem):
    def __init__(self):
        self.providers = ["Telekom", "o2"]
        self.locations = json.load(open("./random_gps.json", "r"))["coordinates"]

    def measure(self) -> Measurement:
        m = Measurement(
            signalStrength=random.randint(-99, -80),
            signalStrengthLTE=random.randint(-99, -80),
            networkProvider=random.choice(self.providers),
            cellId=99999999,
            frequency=random.randint(1, 40),
            gpsNmea=random.choice(self.locations)
        )
        return m

class ModemError(Exception):
    """Modem related error"""
    pass