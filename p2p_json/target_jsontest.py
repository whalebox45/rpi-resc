#!/usr/bin/env python3

import sys 
from time import sleep
import time
from random import randrange

import socket
import json

import threading

from serial import Serial
import pynmea2


sys.path.insert(0, '../')        
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

from SystemInfo import get_serial, get_mac_address



try:
    pf = open('target_info.json','r')
except:
    pf = []
finally:
    pdata = json.load(pf)






def gps_nmea():
    while True:
        global gps_stop
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

            print()
            print(gps)
        
        if gps_stop:
            break


gps_stop = False


hostname = socket.gethostname()
serialno = get_serial()
macaddr = get_mac_address()




BOARD.setup()
parser = LoRaArgumentParser("Continous LoRa receiver.")


class LoRaTarget(LoRa):

    target_data = dict(
                {
                    "Hostname": socket.gethostname(),
                    "SerialNo.": get_serial(),
                    "MACAddress": get_mac_address(),
                    "PersonalData": pdata
                }
            )

    transmit_str = ""
    transmit_queue = ""

    def __init__(self, verbose=False):
        super(LoRaTarget, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        

    def on_rx_done(self):
        self.set_mode(MODE.STDBY)
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        data = [c for c in payload]
        print(payload)
        # print(data)
 
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        
        transmit_partition_len = int(self.get_payload_length()) - 10
        
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        
        self.tx_counter += 1
        
        BOARD.led_off()
        

        if self.transmit_str == "":
            self.transmit_str = f'{self.target_data}'



        # Pop payload queue
        if len(self.transmit_str) > transmit_partition_len:

            self.transmit_queue = self.transmit_str[:transmit_partition_len]
            self.transmit_str = self.transmit_str[transmit_partition_len:]
        else:
            self.transmit_queue = self.transmit_str
            





        print(f"\ntx #{self.tx_counter}: {self.transmit_queue}")

        data = [int(hex(ord(c)), 0) for c in self.transmit_queue]



        self.write_payload(data)
        
        self.transmit_str = ""
        
        BOARD.led_on()

        self.set_mode(MODE.TX)
        sleep(0.25)

    def start(self):
        
        self.tx_counter = 0
        self.reset_ptr_rx()
        while True:
            
            self.set_mode(MODE.STDBY)

            self.set_dio_mapping([0,0,0,0,0,0])
            self.set_mode(MODE.RXCONT)
            print("\nRX mode")

            t_start = time.time()
            t_end = time.time()

            rx_time = randrange(5,11)

            while t_end - t_start <= rx_time:
                rssi_value = self.get_rssi_value()
                status = self.get_modem_status()
                sys.stdout.flush()
                sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
                # sleep(0.1)
                t_end = time.time()

            self.set_mode(MODE.SLEEP)
            sleep(1)
            
            self.target_data = dict(
                {
                    "Hostname": socket.gethostname(),
                    "SerialNo.": get_serial(),
                    "MACAddress": get_mac_address(),
                    "PersonalData": pdata
                }
            )

            print("\nTX mode")
            self.set_dio_mapping([1,0,0,0,0,0])
            self.set_mode(MODE.TX)
            
            sleep(6)
            self.reset_ptr_rx()
            








lora = LoRaTarget(verbose=False)
args = parser.parse_args(lora)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)
lora.set_rx_crc(True)
lora.set_freq(433)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_pa_config(max_power=0, output_power=0)
#lora.set_lna_gain(GAIN.G1)
#lora.set_implicit_header_mode(False)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
#lora.set_agc_auto_on(True)

print(lora)
assert(lora.get_agc_auto_on() == 1)

payload_length = lora.get_payload_length()


gps_thread = threading.Thread(target=gps_nmea)

gps_thread.start()

try:
    lora.start()
    
except KeyboardInterrupt:
    sys.stdout.flush()
    print("")
    sys.stderr.write("KeyboardInterrupt\n")
finally:
    sys.stdout.flush()
    print("")
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()

    gps_stop = True
