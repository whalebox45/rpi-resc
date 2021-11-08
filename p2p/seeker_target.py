
import sys 
from time import sleep
sys.path.insert(0, '..')        
from SX127x.LoRa import *
from SX127x.LoRaArgumentParser import LoRaArgumentParser
from SX127x.board_config import BOARD

class LoRaBeacon(LoRa):
    tx_counter = 0
    
    def __init__(self, verbose=False):
        super(LoRaBeacon, self).__init__(verbose)
        self.set_mode(MODE.SLEEP)
        self.set_dio_mapping([1,0,0,0,0,0])
    
    def on_tx_done(self):
        self.set_mode(MODE.STDBY)
        self.clear_irq_flags(TxDone=1)
        sys.stdout.flush()
        self.tx_counter += 1
        sys.stdout.write("\rtx #%d" % self.tx_counter)
        BOARD.led_off()
        sleep(1)
        rawinput = "transmit ok"
        data = [int(hex(ord(c)), 0) for c in rawinput]
        self.write_payload(data)
        BOARD.led_on()
        self.set_mode(MODE.TX)

    def start(self):
        sys.stdout.write("\rstart")
        self.tx_counter = 0
        BOARD.led_on()
        # self.write_payload([0x0f])
        #self.write_payload([0x0f, 0x65, 0x6c, 0x70])
        self.set_mode(MODE.TX)
        sleep(5)


def main():
    BOARD.setup()
    try:
        parser_t = LoRaArgumentParser("lora beacon")
        lora_t = LoRaBeacon(verbose=False)
        args_t = parser_t.parse_args(lora_t)
        lora_t.set_pa_config(pa_select=1)
        assert(lora_t.get_agc_auto_on() == 1)
        lora_t.start()
        lora_t.set_mode(MODE.SLEEP)
    except KeyboardInterrupt:
        sys.stdout.flush()
        print("")
        sys.stderr.write("KeyboardInterrupt\n")
    finally:
        sys.stdout.flush()
        print("")
        lora_t.set_mode(MODE.SLEEP)
        print(lora_t)
        BOARD.teardown()

while True:
    main()