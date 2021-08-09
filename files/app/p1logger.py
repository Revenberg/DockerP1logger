import configparser
import datetime
import init_db
import os
import binascii
import sys
import decimal
import re
import crcmod.predefined
import serial
import time
import json
from influxdb import InfluxDBClient

config = configparser.RawConfigParser(allow_no_value=True)
config.read("p1logger_config.ini")

do_raw_log = config.getboolean('Logging', 'do_raw_log')

influx_server = config.get('InfluxDB', 'influx_server')
influx_port = int(config.get('InfluxDB', 'influx_port'))
influx_database = config.get('InfluxDB', 'database')
influx_measurement = config.get('InfluxDB', 'measurement')

device = config.get('p1', 'device')
baudrate = config.get('p1', 'baudrate')

values = dict()

crc16 = crcmod.predefined.mkPredefinedCrcFun('crc16')

class SmartMeter(object):

    def __init__(self, port, *args, **kwargs):
        try:
            self.serial = serial.Serial(
                port,
                kwargs.get('baudrate', 115200),
                timeout=10,
                bytesize=serial.SEVENBITS,
                parity=serial.PARITY_EVEN,
                stopbits=serial.STOPBITS_ONE
            )
        except (serial.SerialException,OSError) as e:
            raise SmartMeterError(e)
        else:
            self.serial.setRTS(False)
            self.port = self.serial.name

    def connect(self):
        if not self.serial.isOpen():
            self.serial.open()
            self.serial.setRTS(False)

    def disconnect(self):
        if self.serial.isOpen():
            self.serial.close()

    def connected(self):
        return self.serial.isOpen()

    def read_one_packet(self):
        datagram = b''
        lines_read = 0
        startFound = False
        endFound = False
        max_lines = 35 #largest known telegram has 35 lines

        while not startFound or not endFound:
            try:
                line = self.serial.readline()
            except Exception as e:
                raise SmartMeterError(e)

            lines_read += 1

            if re.match(b'.*(?=/)', line):
                startFound = True
                endFound = False
                datagram = line.lstrip()
            elif re.match(b'(?=!)', line):
                endFound = True
                datagram = datagram + line
            else:
                datagram = datagram + line

            # TODO: build in some protection for infinite loops

        return P1Packet(datagram)

class SmartMeterError(Exception):
    pass

class P1PacketError(Exception):
    pass

class P1Packet(object):
    _datagram = ''
    _datadetails = None
    _keys = {}

    def __init__(self, datagram):

        f = open('p1.json', "r")
        self._datadetails = json.load(f)
        f.close()

        self._datagram = datagram

        self.validate()
        self.split()

    def getItems(self):
        return self.self._keys

    def __getitem__(self, key):
        return self.self._keys[key]


    def get_float(self, regex, default=None):
        result = self.get(regex, None)
        if not result:
            return default
        return float(self.get(regex, default))


    def get_int(self, regex, default=None):
        result = self.get(regex, None)
        if not result:
            return default
        return int(result)


    def get(self, regex, default=None):
        results = re.search(regex, self._datagram, re.MULTILINE)
        if not results:
            return default
        return results.group(1).decode('ascii')


    def validate(self):
        pattern = re.compile(b'\r\n(?=!)')
        for match in pattern.finditer(self._datagram):
            packet = self._datagram[:match.end() + 1]
            checksum = self._datagram[match.end() + 1:]

        if checksum.strip():
            given_checksum = int('0x' + checksum.decode('ascii').strip(), 16)
            calculated_checksum = crc16(packet)

            if given_checksum != calculated_checksum:
                raise P1PacketError('P1Packet with invalid checksum found')

    def split(self):
        self._keys = {}
        pattern = re.compile(b'(.*?)\\((.*?)\\)\r\n')
        for match in pattern.findall(self._datagram):
            key = match[0].decode("utf-8")
            if key in self._datadetails:
                if 'key' in self._datadetails[key]:
                    if do_raw_log:
                        print("found: " + key + " = " + match[1].decode("utf-8") + " : "+ self._datadetails[key]['value'])

                    fieldname = self._datadetails[key]['key']
                    #fieldname = self._datadetails[key]['value']
                    #splitted = fieldname.split(".")
                    #if len(splitted) > 1:
                    #    fieldname = splitted[0]

                    value = match[1].decode("utf-8")
                    splitted = value.split("(")
                    if len(splitted) > 1:
                        value = splitted[1]

                    if 'unit' in self._datadetails[key]:
                        value = value.replace(self._datadetails[key]['unit'], "")

                    if 'type' in self._datadetails[key]:
                        if self._datadetails[key]['type'] == "float":
                            value = float(value)
                    if do_raw_log:
                        print(fieldname)
                        print(value)
                    self._keys[fieldname] = value
            else:
                if do_raw_log:
                    print("not found: " + key + " = " + match[1].decode("utf-8"))

    def __str__(self):
        return self._datagram.decode('ascii')

def getData(device, baudrate):

    meter = SmartMeter(device, baudrate)

    while True:
        values = meter.read_one_packet()        

        if do_raw_log:
            print( values )

        json_body = {'points': [{
                            'fields': {k: v for k, v in values._keys.items()}
                                }],
                        'measurement': influx_measurement
                    }

        if do_raw_log:
            print( json.dumps(json_body) )
            sys.stdout.flush()

        client = InfluxDBClient(host=influx_server,
                        port=influx_port)

        success = client.write(json_body,
                            # params isneeded, otherwise error 'database is required' happens
                            params={'db': influx_database})

        if not success:
            print('error writing to database')

        time.sleep(60)

def openDatabase():
    # if the db is not found, then try to create it
    try:
        dbclient = InfluxDBClient(host=influx_server, port=influx_port )
        dblist = dbclient.get_list_database()
        db_found = False
        for db in dblist:
            if db['name'] == influx_database:
                db_found = True
        if not(db_found):
            print( dbclient.get_list_continuous_queries())
            sys.exit('Database ' + influx_database + ' not found, create it')

    except Exception as e:
        print(e)
        sys.exit('Error querying open influx_server: ' + influx_server)

openDatabase()

getData(device, baudrate)