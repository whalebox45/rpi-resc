from enum import Enum, unique
import threading
import time, datetime
import json

from LoraRescuer import LoraRescuer

import socket

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



def socket_new_setup():
    confp = configparser.ConfigParser()
    confp.read('targ-wifi.conf')
    try:
        SOCKET_HOST = confp['wifi']['port']
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







def socket_setup():
    """Socket伺服器連線對象設置，讀取config檔案，若失敗則用hardcode"""
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

    global client_sock
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global wifi_addr
    wifi_addr = (SOCKET_HOST,SOCKET_PORT)

def sock_recv_udp():
    while True:
        global sock_message_recv
        sock_message_recv, addr = client_sock.recvfrom(1024)
        print("Socket RX: %s" % sock_message_recv.decode())

def sock_write_udp():
    message_send = str(MessageFormat())
    client_sock.sendto(message_send.encode(), wifi_addr)
    print("Socket TX: %s" % message_send)
    time.sleep(1)











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

    time.sleep(5)

def lora_sleep(lora:LoraRescuer):
    lora.set_mode(MODE.SLEEP)

@unique
class TargetMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2





current_mode = TargetMode.LORA
if WIFI_SOCKET_TEST: current_mode = TargetMode.WIFI


current_time = datetime.datetime.now()

rx_ok_count = 0
rx_fail_count = 0


def main():
    while True:
        global current_mode, rx_ok_count, current_time
        stored_msg = object()
        while current_mode == TargetMode.LORA:

            fetched_time = current_time
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
                print(f'rx_ok_count: {rx_ok_count}')
            
            '''
                TODO 如果計數器數值數值足夠大就切換至 DUAL 模式
                暫時設為 WIFI 模式
            '''
            if rx_ok_count >= 5:
                current_mode = TargetMode.WIFI
                print('Change to WIFI Mode')
                rx_ok_count = 0

        while current_mode == TargetMode.DUAL:
            pass

        while current_mode == TargetMode.WIFI:
            lora_sleep(lora)
            fetched_time = current_time
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
                
            
            if stored_msg == jrx:
                pass

            """
                TODO 測試用：WIFI模式500次成功時返回LORA
            """
            if rx_ok_count >= 500:
                current_mode = TargetMode.LORA
                print('Change to LORA mode')
                rx_ok_count = 0



print('socket setup')
# socket_setup()   
# recv_udp_thread = threading.Thread(target=sock_recv_udp)
# write_udp_thread = threading.Thread(target=sock_write_udp)
# recv_udp_thread.setDaemon(True)
# recv_udp_thread.start()



socket_new_setup()

recv_udp_thread = threading.Thread(target=sock_targ.recv_udp)
recv_udp_thread.setDaemon(True)
recv_udp_thread.start()

lora_setup()



def timer():
    while True:
        global current_time
        current_time = datetime.datetime.now()
        # print(datetime.datetime.time(current_time))
        time.sleep(0.5)


timer_thread = threading.Thread(target=timer)
timer_thread.setDaemon(True)



time.sleep(3)




try:
    main()
except KeyboardInterrupt as ke:
    sys.stderr.write(ke)
finally:
    lora.set_mode(MODE.SLEEP)
    print(lora)
    BOARD.teardown()
