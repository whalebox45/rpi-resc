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

from SocketTarget import SocketTarget

argp = argparse.ArgumentParser()
argp.add_argument("-w","--wifi",action="store_true")
args = argp.parse_args()

WIFI_SOCKET_TEST = False
if args.wifi: WIFI_SOCKET_TEST = True


@unique
class TargetMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2


current_mode = TargetMode.LORA
if WIFI_SOCKET_TEST: current_mode = TargetMode.WIFI



def socket_new_setup():
    confp = configparser.ConfigParser()
    confp.read('targ-wifi.conf')
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
    
    global sock_targ
    sock_targ = SocketTarget(SOCKET_HOST,SOCKET_PORT)
    print("socket start")
    print(sock_targ)





def lora_setup():
    """LoRa 模組設置"""
    BOARD.setup()

    """ TODO 此處先共用LoraRescuer"""
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
        # print(datetime.datetime.time(current_time))
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
            LORA 模式
        =========================================="""
        while current_mode == TargetMode.LORA:

            lora_tx(lora,str(MessageFormat()))
            lora_rx(lora)

            try:
                rd = lora.rx_data
                print(rd)
                jrx = json.loads(rd.replace("\'","\""))
                ser = jrx['MessageID']
                print(f'messageid: {ser}')
            except json.JSONDecodeError as jse:
                jrx = stored_msg
            except Exception as e:
                jrx = stored_msg

            if stored_msg != jrx:
                stored_msg = jrx
                rx_ok_count += 1
                rx_ok_time = current_time
                print(f'rx_ok_count: {rx_ok_count}')
            
            """
                如果在規定時間內都沒有收到LoRa訊息，就重設計數器數值
            """


            if (current_time - rx_ok_time).seconds >= 33:
                print("reset rx_ok_count to 0")
                rx_ok_count = 0
                rx_ok_time = current_time


            '''
                TODO 如果計數器數值數值足夠大就切換至 DUAL 模式
                暫時設為 WIFI 模式
            '''
            if rx_ok_count >= 5:
                current_mode = TargetMode.WIFI
                print('Change to WIFI Mode')
                rx_ok_count = 0
                rx_ok_time = current_time





        """==========================================
            DUAL 模式
        =========================================="""
        while current_mode == TargetMode.DUAL:
            pass


        """==========================================
            WIFI 模式
        =========================================="""
        while current_mode == TargetMode.WIFI:
            lora_sleep(lora)

            sock_targ.write_udp(str(MessageFormat()))
            # sock_write_udp()
            try:
                rd = sock_targ.rx_data
                # rd = sock_message_recv.decode()
                print(rd)
                jrx = json.loads(rd.replace("\'","\""))
                ser = jrx['MessageID']
                print(f'messageid: {ser}')
            except json.JSONDecodeError as jse:
                jrx = stored_msg
            except Exception as e:
                jrx = stored_msg

            if stored_msg != jrx:
                stored_msg = jrx
                rx_ok_count += 1
                print(f'rx_ok_count: {rx_ok_count}')
                


            
            """
                超過五秒沒接收到新的，則視為接收失敗一次
            """
            if (current_time - rx_ok_time).seconds >= 7:
                rx_fail_count += 1
                print(f'rx_fail_count: {rx_fail_count}')
                rx_ok_count = 0
                rx_ok_time = current_time




            """
                TODO 測試用：WIFI模式10次成功時返回LORA
            """
            if rx_ok_count >= 10:
                current_mode = TargetMode.LORA
                print('Change to LORA mode')
                rx_ok_count = 0

            """
                連續接收失敗五次，返回DUAL模式
                TODO 測試用：此處先返回至LORA模式
            """
            if rx_fail_count >= 5:
                current_mode = TargetMode.LORA
                print('Fail: Change to LORA mode')
                rx_ok_count = 0
                rx_fail_count = 0



print('socket setup')
socket_new_setup()

recv_udp_thread = threading.Thread(target=sock_targ.recv_udp)
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
