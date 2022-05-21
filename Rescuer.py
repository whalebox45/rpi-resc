

from enum import Enum, unique
import threading
import time, datetime

from LoraRescuer import LoraRescuer

from MessageFormat import MessageFormat

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

def lora_setup():
    """LoRa 模組設置"""
    BOARD.setup()
    parser = LoRaArgumentParser("Continous LoRa receiver.")

    global lora
    lora = LoraRescuer(verbose=False)  

    args = parser.parse_args(lora)

    lora.set_mode(MODE.STDBY)
    lora.set_pa_config(pa_select=1)
    lora.set_rx_crc(True)
    lora.set_freq(433)
    print(lora)
    assert(lora.get_agc_auto_on() == 1)








def lora_rx(lora:LoraRescuer):
    """將LoRa設為MODE.RXCONT"""
    lora.reset_ptr_rx()
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([0,0,0,0,0,0])
    lora.set_mode(MODE.RXCONT)

    # Sleep
    lora.set_mode(MODE.SLEEP)
    time.sleep(0.5)

def lora_tx(lora:LoraRescuer,message:str):
    lora.tx_data = message
    """將LoRa設為MODE.TX，並且以message參數傳入訊息內容"""
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_mode(MODE.TX)

    lora.reset_ptr_rx()

    # Sleep
    lora.set_mode(MODE.SLEEP)
    time.sleep(0.5)


@unique
class RescuerMode(Enum):
    LORA = 0
    DUAL = 1

current_mode = RescuerMode.LORA

rx_counter = 0


current_time = datetime.datetime.now()
def timer():
    while True:
        global current_time
        current_time = datetime.datetime.now()
        print(datetime.datetime.time(y))
        time.sleep(0.5)
            



def main():
    while current_mode == RescuerMode.LORA:
        lora_rx(lora)
        '''
            如果在規定時間內收到LoRa訊息，增加計數器數值，並且發送自身的LoRa訊息
        '''
        if True:
        # if get_message_in10sec:
            rx_counter += 1
            lora_tx(lora,MessageFormat())

        '''
            如果在規定時間內都沒有收到LoRa訊息，就重設計數器數值
        '''
        
        # if lost_message_in10sec:
        #     rx_counter = 0
        
        '''
            如果計數器數值數值足夠大就切換至 DUAL 模式
        '''
        if rx_counter >= 5:
            current_mode = RescuerMode.DUAL
            print('Change to DUAL Mode')
            current_mode = RescuerMode.LORA
            rx_counter = 0



lora_setup()
timer_thread = threading.Thread(target=timer)
timer_thread.setDaemon(True)

try:
    main()
except KeyboardInterrupt as ke:
    sys.stderr.write(ke)
finally:
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()