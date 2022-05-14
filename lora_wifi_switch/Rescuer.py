import sys
import threading
import time

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

from LoRaRescuer import LoRaRescuer, LoRaSignalMode, lora_receive, lora_start, lora_transmit


BOARD.setup()
parser = LoRaArgumentParser("Continous LoRa receiver.")

lora = LoRaRescuer(verbose=False)
args = parser.parse_args(lora)

lora.set_mode(MODE.STDBY)
lora.set_pa_config(pa_select=1)
lora.set_rx_crc(True)
lora.set_freq(433)
print(lora)
assert(lora.get_agc_auto_on() == 1)


def TimerControl():
    while True:
        lora.mode_switch = LoRaSignalMode.rx
        time.sleep(5)
        lora.mode_switch = LoRaSignalMode.tx
        time.sleep(5)

timer_control_thread = threading.Thread(target=TimerControl)
timer_control_thread.setDaemon(True)

try:
    timer_control_thread.start()
    while True:
        lora_receive(lora)
        lora_transmit(lora)
        
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
