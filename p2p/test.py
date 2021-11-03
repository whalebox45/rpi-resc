import sys
from time import sleep, time
import threading

sys.path.insert(0, '..')
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

    def start(self):
        BOARD.led_off()

        while True:

            self.reset_ptr_rx()
            self.set_mode(MODE.RXCONT)
            sleep(.5)
            rssi_value = self.get_rssi_value()
            status = self.get_modem_status()
            sys.stdout.flush()
            sys.stdout.write("\r%d %d %d" % (rssi_value, status['rx_ongoing'], status['modem_clear']))
    



class TimeCount(threading.Thread):
    time_kill = False
    
    def __init__(self):
        threading.Thread.__init__(self)
    
    def kill(self):
        self.time_kill = True

    def run(self):
        while True:
            if self.time_kill: return
            print("Time: 5s")
            sleep(5)
            








lora = LoRaP2P(verbose=False)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)

print(lora)
assert(lora.get_agc_auto_on() == 1)

tc = TimeCount()




try:
    tc.start()
    lora.start()
except (KeyboardInterrupt, SystemExit):
    sys.stdout.flush()
finally:
    tc.kill()
    sys.stdout.flush()
    lora.set_mode(MODE.SLEEP)
    BOARD.teardown()

