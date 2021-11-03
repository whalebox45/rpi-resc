from serial import Serial
import time
import pynmea2

while True:
    port="/dev/ttyAMA0"
    ser= Serial(port, baudrate=9600, timeout=0.5)
    dataout = pynmea2.NMEAStreamReader()
    newdata = ser.readline()
    if newdata[0:6] == "$GPRMC":
        print(newdata)
        newmsg = pynmea2.parse(newdata)
        lat = newmsg.latitude
        lng = newmsg.longitude
        gps = "Lat: " + f'{lat}' + "Lng: " + f'{lng}'
        print(gps)