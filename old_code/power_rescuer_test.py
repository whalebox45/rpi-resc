

from enum import Enum, unique
import threading
import time, datetime
import json

from LoraRescuer import LoraRescuer

from MessageFormat import MessageFormat

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser
 
import argparse, configparser

from SocketRescuer import SocketRescuer

argp = argparse.ArgumentParser()
argp.add_argument("-w","--wifi",action="store_true")
argp.add_argument("-d","--dual",action="store_true")
argp.add_argument("-t","--test",action="store_true")
args = argp.parse_args()

@unique
class RescuerMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2


current_mode = RescuerMode.DUAL


if args.test: TESTMODE = True
else: TESTMODE = False



def socket_new_setup():
    confp = configparser.ConfigParser()
    confp.read('resc-wifi.conf')
    try:   
        SOCKET_HOST = confp['wifi']['host']
    except:
        print('Fallback: Hardcode Address')
        SOCKET_HOST = '192.168.4.1'

    try:
        SOCKET_PORT = int(confp['wifi']['port'])
    except:
        print('Fallback: Hardcode Port')
        SOCKET_PORT = 8763

    global sock_resc
    sock_resc = SocketRescuer(SOCKET_HOST,SOCKET_PORT)
    print("socket start")
    print(sock_resc)





def lora_setup():
    """LoRa 模組設置"""
    BOARD.setup()

    global lora
    lora = LoraRescuer()  


    lora.set_mode(MODE.STDBY)
    lora.set_pa_config(pa_select=1)
    lora.set_rx_crc(True)
    lora.set_freq(433)
    print(lora)
    assert(lora.get_agc_auto_on() == 1)




def lora_rx(lora:LoraRescuer):
    """將LoRa設為MODE.RXCONT"""
    lora.set_dio_mapping([0,0,0,0,0,0])
    lora.set_mode(MODE.RXCONT)

    time.sleep(5)

def lora_tx(lora:LoraRescuer,message:str):
    """將LoRa設為MODE.TX，並且以message參數傳入訊息內容"""
    lora.tx_data = message
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_mode(MODE.TX)

    time.sleep(6)


def lora_sleep(lora:LoraRescuer):
    lora.set_mode(MODE.SLEEP)


current_time = datetime.datetime.now()

def timer():
    print("timer activated")
    while True:
        global current_time
        current_time = datetime.datetime.now()
        print(datetime.datetime.time(current_time))
        time.sleep(0.5)


timer_thread = threading.Thread(target=timer)
timer_thread.setDaemon(True)
timer_thread.start()



rx_ok_count = 0
rx_fail_count = 0



def main():
    global current_mode, rx_ok_count, rx_fail_count, current_time
    stored_msg = object()
    rx_ok_time = current_time
    while True:

        """==========================================
            DUAL 模式
        =========================================="""
        while current_mode == RescuerMode.DUAL:
            
            lora_rx(lora)
            try:
                lrd = lora.rx_data
                ljrx = json.loads(lrd.replace("\'","\""))
                print(f"messageid: {ljrx['MessageID']}")
            except:
                ljrx = stored_msg
            
            try:
                srd = sock_resc.rx_data
                sjrx = json.loads(srd.replace("\'","\""))
                print(f"messageid: {sjrx['MessageID']}")
            except:
                sjrx = stored_msg
            

            if stored_msg != sjrx:
                print(f"messageid: {sjrx['MessageID']}")
                stored_msg = sjrx
                rx_ok_count += 1
                rx_fail_count = 0
                print(f'rx_ok_count: {rx_ok_count}')
                rx_ok_time = current_time


            """
            超過15秒沒接收到新的，則視為接收失敗一次
            """
            if (current_time - rx_ok_time).seconds >= 15:
                rx_ok_count = 0
                rx_fail_count += 1
                print(f'rx_fail_count: {rx_fail_count}')
                rx_ok_time = current_time

            fetch_msg = str(MessageFormat())
            lora_tx(lora,fetch_msg)
            for i in range(5):
                sock_resc.write_udp(fetch_msg)

            """
            如果計數器數值數值足夠大就切換至 WIFI 模式    
            """
            if rx_ok_count >= 5:
                current_mode = RescuerMode.DUAL
                print('OK: Change to DUAL Mode')
                rx_ok_count = 0
                rx_fail_count = 0
                rx_ok_time = current_time
                break
            """
            連續接收失敗五次，返回 LORA 模式    
            """
            if rx_fail_count >= 5:
                current_mode = RescuerMode.DUAL
                print('Fail: Change to DUAL mode')
                rx_ok_count = 0
                rx_fail_count = 0
                rx_ok_time = current_time




print('socket setup')
socket_new_setup()

recv_udp_thread = threading.Thread(target=sock_resc.recv_udp)
recv_udp_thread.setDaemon(True)
recv_udp_thread.start()

lora_setup()

time.sleep(3)

try:  
    main()
except KeyboardInterrupt as ke:
    sys.stderr.write(str(ke))
finally:
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()
