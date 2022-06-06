from enum import Enum, unique
import threading
import time, datetime
import json

from LoraRescuer import LoraRescuer

from TargetMsgFormat import TargetMsgFormat, gps_signal

from SX127x.LoRa import *
from SX127x.board_config import BOARD
from SX127x.LoRaArgumentParser import LoRaArgumentParser

import argparse, configparser

from SocketTarget import SocketTarget

argp = argparse.ArgumentParser()
argp.add_argument("-w","--wifi",action="store_true")
argp.add_argument("-d","--dual",action="store_true")
args = argp.parse_args()



@unique
class TargetMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2


current_mode = TargetMode.LORA
if args.wifi: current_mode = TargetMode.WIFI
elif args.dual: current_mode = TargetMode.DUAL



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

    """此處共用LoraRescuer"""
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

            lora_tx(lora,str(TargetMsgFormat()))
            lora_rx(lora)
            """
            如果在規定時間內收到LoRa訊息，增加計數器數值，並且發送自身的LoRa訊息
            """
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


            """
            如果計數器數值數值足夠大就切換至 DUAL 模式    
            """
            if rx_ok_count >= 5:
                current_mode = TargetMode.DUAL
                print('Change to DUAL Mode')
                rx_ok_count = 0
                rx_fail_count = 0
                rx_ok_time = current_time
                break





        """==========================================
            DUAL 模式
        =========================================="""
        while current_mode == TargetMode.DUAL:
            
            fetch_msg = str(TargetMsgFormat())
            lora_tx(lora,fetch_msg)
            for i in range(5):
                sock_targ.write_udp(fetch_msg)

            lora_rx(lora)
            try:
                lrd = lora.rx_data
                ljrx = json.loads(lrd.replace("\'","\""))
                print(f"messageid: {ljrx['MessageID']}")
            except:
                ljrx = stored_msg
            
            try:
                srd = sock_targ.rx_data
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
            超過20秒沒接收到新的，則視為接收失敗一次
            """
            if (current_time - rx_ok_time).seconds >= 20:
                rx_ok_count = 0
                rx_fail_count += 1
                print(f'rx_fail_count: {rx_fail_count}')
                rx_ok_time = current_time
            

            """
            如果計數器數值數值足夠大就切換至 WIFI 模式    
            """
            if rx_ok_count >= 5:
                current_mode = TargetMode.WIFI
                print('Change to WIFI Mode')
                rx_ok_count = 0
                rx_fail_count = 0
                rx_ok_time = current_time
                break
            
            """
            連續接收失敗五次，返回 LORA 模式    
            """
            if rx_fail_count >= 5:
                current_mode = TargetMode.LORA
                print('Fail: Change to LORA mode')
                rx_ok_count = 0
                rx_fail_count = 0
                rx_ok_time = current_time






        """==========================================
            WIFI 模式
        =========================================="""
        while current_mode == TargetMode.WIFI:
            lora_sleep(lora)

            sock_targ.write_udp(str(TargetMsgFormat(getPersonalData=True)))
            # sock_write_udp()
            try:
                rd = sock_targ.rx_data
                jrx = json.loads(rd.replace("\'","\""))
                
            except json.JSONDecodeError as jse:
                jrx = stored_msg
            except Exception as e:
                jrx = stored_msg

            if stored_msg != jrx:
                print(f"messageid: {jrx['MessageID']}")
                stored_msg = jrx
                rx_ok_count += 1
                rx_fail_count = 0
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
                rx_fail_count = 0
                break

            """
            連續接收失敗五次，返回DUAL模式    
            """
            if rx_fail_count >= 5:
                current_mode = TargetMode.DUAL
                print('Fail: Change to DUAL mode')
                rx_ok_count = 0
                rx_fail_count = 0



TargetMsgFormat.gps_signal = staticmethod(TargetMsgFormat.gps_signal)

print('GPS setup')
gps_signal_thread = threading.Thread(target=TargetMsgFormat.gps_signal)
gps_signal_thread.setDaemon(True)
gps_signal_thread.start()

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
