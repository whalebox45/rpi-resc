#!/usr/bin/env python3

import time
from random import randrange

import sys
     
from SX127x.LoRa import *

from SystemInfo import get_serial, get_mac_address, get_hostname

rescuer_data = dict({
    "Hostname": get_hostname(),
    "SerialNo.": get_serial(),
    "MACAddress": get_mac_address()
    }
)


class LoRaRescuer(LoRa):

    def __init__(self, verbose=False):
        super(LoRaRescuer, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])
        

    def on_rx_done(self):
        BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        data = ''.join([chr(c) for c in payload])
        
        # print(payload)
        print(f'\n{data}')
 
        # self.reset_ptr_rx()
        BOARD.led_off()
        # self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        
        self.tx_counter += 1
        
        BOARD.led_off()
        
        
        transmit_str = f'{rescuer_data}'

        print(f"\ntx #{self.tx_counter}: {transmit_str}")

        data = [ord(c) for c in transmit_str]

        self.write_payload(data)
        BOARD.led_on()
        self.set_mode(MODE.TX)
        time.sleep(0.25)

def lora_start(lora:LoRa):
    
    lora.tx_counter = 0
    lora.reset_ptr_rx()
    while True:
        
        lora.set_mode(MODE.STDBY)

        lora.set_dio_mapping([0,0,0,0,0,0])
        lora.set_mode(MODE.RXCONT)
        
        # Start RX mode
        print("\nRX mode")

        t_start = time.time()
        t_end = time.time()
        rx_time = randrange(5,11)

        # RX mode in 5~11 seconds
        while t_end - t_start <= rx_time:
            rssi_value = lora.get_rssi_value()
            status = lora.get_modem_status()
            sys.stdout.flush()
            sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
            
            t_end = time.time()


        # Sleep 1 second and switch to TX mode
        lora.set_mode(MODE.SLEEP)
        time.sleep(1)
        print("\nTX mode")
        lora.set_dio_mapping([1,0,0,0,0,0])
        lora.set_mode(MODE.TX)
        
        # TX mode in 6 seconds
        time.sleep(6)
        lora.reset_ptr_rx()