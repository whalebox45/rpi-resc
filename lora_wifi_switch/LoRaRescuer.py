#!/usr/bin/env python3

from enum import Enum, unique
from random import randrange
import sys
import time

from SX127x.LoRa import *

from SystemInfo import get_serial, get_mac_address, get_hostname

rescuer_data = dict({
    "Hostname": get_hostname(),
    "SerialNo.": get_serial(),
    "MACAddress": get_mac_address()
    }
)

@unique
class LoRaSignalMode(Enum):
    blank = 0
    rx = 1
    tx = 2
    stdby = 3


class LoRaRescuer(LoRa):

    tx_string = str("")
    rx_string = str("")

    def __init__(self, verbose=False):
        super(LoRaRescuer, self).__init__(verbose)

        self.mode_switch = LoRaSignalMode.blank
        self.transmit_str = str("")
        
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])

        
        self.reset_ptr_rx()
        

    def on_rx_done(self):
        self.set_mode(MODE.RXCONT)
        # BOARD.led_on()
        print("\nRxDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        data = ''.join([chr(c) for c in payload])
        
        # print(payload)
        self.rx_string = data
        print(self.rx_string)

        # self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.STDBY)

    def on_tx_done(self):
        
        # self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        
        
        
        # BOARD.led_off()
        
        
        transmit_str = f'{rescuer_data}'

        print(f"\n{transmit_str}")

        data = [ord(c) for c in transmit_str]

        self.write_payload(data)
        # BOARD.led_on()
        self.set_mode(MODE.TX)
        time.sleep(1)





def lora_receive(lora:LoRaRescuer,verbose=False):

    lora.reset_ptr_rx()
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([0,0,0,0,0,0])
    lora.set_mode(MODE.RXCONT)
    
    print("\nRX mode")

    # Keep in receive mode when it's not switched
    while lora.mode_switch is LoRaSignalMode.rx:

        if verbose:
            rssi_value = lora.get_rssi_value()
            status = lora.get_modem_status()
            sys.stdout.flush()
            sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
        

    # Sleep 1 second
    lora.set_mode(MODE.SLEEP)
    time.sleep(0.5)






def lora_transmit(lora:LoRaRescuer):
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_mode(MODE.TX)
    
    print("\nTX mode")

    # Keep in transmit mode when it's not switched
    while lora.mode_switch is LoRaSignalMode.tx:
        time.sleep(1)

    lora.reset_ptr_rx()

    # Sleep 1 second
    lora.set_mode(MODE.SLEEP)
    time.sleep(0.5)
