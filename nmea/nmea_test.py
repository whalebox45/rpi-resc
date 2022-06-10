from serial import Serial
import pynmea2

while True:
    try:
        port = "/dev/ttyAMA0"
        ser = Serial(port, baudrate=9600, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata = ser.readline()
        # print(newdata)

        
        if newdata[0:6] == b"$GPRMC":
            newmsg = pynmea2.parse(newdata.decode('ascii'))
            lat = newmsg.latitude
            lng = newmsg.longitude
            gps = "Lat: " + f'{lat}' + "Lng: " + f'{lng}'
            print(gps)
    except:
        pass