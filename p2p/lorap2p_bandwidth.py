#!/usr/bin/env python3

""" A simple continuous receiver class. """
import sys 
from time import sleep
import time
from datetime import timedelta
from socket import gethostname as socket_hostname
sys.path.insert(0, '../')        
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

BOARD.setup()

parser = LoRaArgumentParser("Continous LoRa receiver.")

try:
    w1000_file = open('W1000.txt','rb')
    w1000 = w1000_file.read()
except FileNotFoundError as fe:
    w1000 = str(fe)

try:
    transmit_log = open('tx_log.txt','w+')
except Exception as e:
    print(e)
    exit(1)

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
        print(data)
 
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def on_tx_done(self):
        
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        
        self.tx_counter += 1
        print("tx #%d" % self.tx_counter)
        transmit_log.write("tx #%d\n" % self.tx_counter)
        
        BOARD.led_off()
        sleep(4)
        
        # test_str = f'transmitted from {socket_hostname()}'
        # print(test_str)
        # data = [int(hex(ord(c)), 0) for c in test_str]
        

        w1000_str = w1000.decode()
        # print(test_str)

        data = [x for x in w1000]
        transmit_log.write(w1000_str)

        self.write_payload(data)
        BOARD.led_on()
        self.set_mode(MODE.TX)

    def start(self):
        
        self.tx_counter = 0
        self.reset_ptr_rx()
        while True:
            
            self.set_dio_mapping([0,0,0,0,0,0])
            self.set_mode(MODE.RXCONT)
            print("\nRX mode")

            t_start = time.time()
            t_end = time.time()

            while t_end - t_start < 3:
                rssi_value = self.get_rssi_value()
                status = self.get_modem_status()
                sys.stdout.flush()
                sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
                # sleep(0.5)
                t_end = time.time()

            sleep(0.5)
            # self.reset_ptr_rx()
            self.set_mode(MODE.STDBY)


            print("\nTX mode")
            self.set_dio_mapping([1,0,0,0,0,0])
            self.set_mode(MODE.TX)
            
            sleep(8)



lora = LoRaRcvCont(verbose=False)
args = parser.parse_args(lora)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)
#lora.set_rx_crc(True)
#lora.set_coding_rate(CODING_RATE.CR4_6)
#lora.set_pa_config(max_power=0, output_power=0)
#lora.set_lna_gain(GAIN.G1)
#lora.set_implicit_header_mode(False)
#lora.set_low_data_rate_optim(True)
#lora.set_pa_ramp(PA_RAMP.RAMP_50_us)
#lora.set_agc_auto_on(True)

print(lora)
assert(lora.get_agc_auto_on() == 1)

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
    w1000_file.close()
    transmit_log.close()
