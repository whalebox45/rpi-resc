import json
import uuid
import socket
import serial
import pynmea2

MESSAGE_SERIAL = 0


LATITUDE = 0
LONGITUTE = 0

def gps_signal():
    stored_lat, stored_lng = 0, 0
    while True:
        port = "/dev/ttyAMA0"
        ser = serial.Serial(port, baudrate=9600, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        global LATITUDE, LONGITUTE
        try:
            newdata = ser.readline()
            if newdata[0:6] == b"$GPRMC":
                newmsg = pynmea2.parse(newdata.decode('ascii'))
                LATITUDE = newmsg.latitude
                LONGITUTE = newmsg.longitude
                stored_lat = newmsg.latitude
                stored_lng = newmsg.longitude

        except Exception:
            LATITUDE = stored_lat
            LONGITUTE = stored_lng
            pass



def get_cpuid():
    cpuserial = "000000000000000"
    try:
        cf = open('/proc/cpuinfo','r')
        for line in cf:
            if line[0:6] == 'Serial':
                cpuserial = line[10:26]
        cf.close()
    except:
        cpuserial = "ERROR0000000000"
    return cpuserial



def get_mac_address(hasColon=False):
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    if hasColon:
        return ":".join([mac[e:e+2] for e in range(0,11,2)])
    else: return str(mac)

def get_hostname():
    return socket.gethostname()

def get_serial():
    global MESSAGE_SERIAL
    MESSAGE_SERIAL+= 1
    return MESSAGE_SERIAL

try:
    pf = open('target_info.json','r')
except:
    print('Personal Data file target_info.json not found: leave blank')
    pf = []
finally:
    pdata = json.load(pf)


class TargetMsgFormat():
    def __init__(self,getPersonalData=False):
        self.getPersonalData = getPersonalData
        self.cpuid = get_cpuid()
        self.macaddr = get_mac_address()
        self.hostname = get_hostname()
        self.serial = get_serial()
        if getPersonalData:
            self.pdata = pdata
    
    def __str__(self):
        if self.getPersonalData:
            data_dict = dict({
                "Latitude": LATITUDE,
                "Longitude": LONGITUTE,
                "MessageID": self.serial,
                "CPUSerial": self.cpuid,
                "MACAddr": self.macaddr,
                "Hostname": self.hostname,
                "PersonalData": pdata
            })
        else:
            data_dict = dict({
                "Latitude": LATITUDE,
                "Longitude": LONGITUTE,
                "MessageID": self.serial,
                "CPUSerial": self.cpuid,
                "MACAddr": self.macaddr,
                "Hostname": self.hostname,
            })
        return str(data_dict)

    