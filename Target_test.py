from enum import Enum, unique
import threading
import time, datetime
import json

from LoraRescuer import LoraRescuer

from MessageFormat import MessageFormat

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

def lora_setup()
    """LoRa 模組設置"""
    BOARD.setup()
    parser = LoRaArgumentParser("Continuous LoRa receiver")

    """ TODO 此處先共用LoraRescuer"""
    global lora
    lora = LoraRescuer()

    args = parser.parse_args(lora)

    lora.set_mode(MODE.STDBY)
    lora.set_pa_config(pa_select=1)
    lora.set_rx_crc(True)
    lora.set_freq(433)
    print(lora)
    assert(lora.get_agc_auto_on() == 1)

def lora_rx(lora:LoraRescuer):
    lora.set_dio_mapping([0,0,0,0,0,0])
    lora.set_mode(MODE.RXCONT)

    time.sleep(5)

def lora_tx(lora:LoraRescuer,message:str):
    lora.tx_data = message
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_mode(MODE.TX)

    time.sleep(5)

@unique
class TargetMode(Enum):
    LORA = 0
    DUAL = 1

current_mode = TargetMode.LORA
current_time = datetime.datetime.now()

rx_counter = 0

def timer():
    while True:
        global current_time
        current_time = datetime.datetime.now()
        # print(datetime.datetime.time(current_time))
        time.sleep(0.5)

def main():
    global current_mode, rx_counter, current_time
    stored_msg = object()
    while current_mode == TargetMode.LORA:

        fetched_time = current_time
        lora_tx(lora,str(MessageFormat()))

        lora_rx(lora)


lora_setup()

try:
    main()
except KeyboardInterrupt as ke:
    sys.stderr.write(ke)
finally:
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()
