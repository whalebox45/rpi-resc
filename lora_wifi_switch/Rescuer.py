<<<<<<< HEAD
=======
from enum import Enum, unique
import sys
import threading
import time


>>>>>>> 042d98e237ad844265bb18d496c9defcda95c8d8
from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

from LoRaRescuer import LoRaRescuer, lora_start

import sys


BOARD.setup()
parser = LoRaArgumentParser("Continous LoRa receiver.")

lora = LoRaRescuer(verbose=False)
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

receive_counter = 0

'''
    建立一個時間控制的執行續，透過這個執行緒來控制LoRa收發和WiFi的
    收發模式切換
    TODO 當接收到切換模式的訊號資料時切換至該模式
'''

@unique
class RescuerMode(Enum):
    blank = 0
    lora = 1
    wifi = 2

current_mode = RescuerMode.lora


def TimerControl():
    if current_mode == RescuerMode.lora:
        while True:
            lora.mode_switch = LoRaSignalMode.rx
            time.sleep(5)
            lora.mode_switch = LoRaSignalMode.tx
            time.sleep(5)




timer_control_thread = threading.Thread(target=TimerControl)
timer_control_thread.setDaemon(True)        

'''
    TODO 需要一個自動開啟和關閉WiFi連線的方法
'''



















try:
    lora_start(lora)
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
