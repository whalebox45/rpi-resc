#!/usr/bin/env python3

import sys 
from time import sleep
import time
from random import randrange

import socket
import uuid
import json

from serial import Serial
import pynmea2


sys.path.insert(0, '../')        
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD





def get_serial():
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





hostname = socket.gethostname()
serialno = get_serial()
macaddr = get_mac_address()



BOARD.setup()
parser = LoRaArgumentParser("Continous LoRa receiver.")


class LoRaRcvCont(LoRa):
    def __init__(self, verbose=False):
        super(LoRaRcvCont, self).__init__(verbose)
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
        
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        
        self.tx_counter += 1
        
        BOARD.led_off()
        
        
        transmit_str = f'{target_data}'

        print(f"\ntx #{self.tx_counter}: {transmit_str}")

        data = [int(hex(ord(c)), 0) for c in transmit_str]

        self.write_payload(data)
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
            
            target_data = dict(
                {
                    "Hostname": socket.gethostname(),
                    "SerialNo.": get_serial(),
                    "MACAddress": get_mac_address(),
                }
            )

            print("\nTX mode")
            self.set_dio_mapping([1,0,0,0,0,0])
            self.set_mode(MODE.TX)
            
            sleep(6)
            self.reset_ptr_rx()
            








lora = LoRaRcvCont(verbose=False)
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


    