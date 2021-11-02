import sys
from time import sleep, time
import threading


from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

BOARD.setup()

class LoRaP2P(LoRa):

    def __init__(self, verbose=False):
        super(LoRaP2P, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([0,0,0,0,0,0])

    # Override on_rx_done
    def on_rx_done(self):
        BOARD.led_on()
        print("\nRXDone")
        self.clear_irq_flags(RxDone=1)
        payload = self.read_payload(nocheck=True)
        print(payload)
        self.set_mode(MODE.SLEEP)
        self.reset_ptr_rx()
        BOARD.led_off()
        self.set_mode(MODE.RXCONT)

    def time_count(self):
        while True:
            print("Time: 5s")
            sleep(5)

    def start(self):
        BOARD.led_off()
        tc = threading.Thread(target=self.time_count)
        
        tc.start()
        while True:
            

            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sleep(.5)
    