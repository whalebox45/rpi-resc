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

argp = argparse.ArgumentParser()
argp.add_argument("-w","--wifi",action="store_true")
args = argp.parse_args()

WIFI_SOCKET_TEST = False
if args.wifi: WIFI_SOCKET_TEST = True





def socket_setup():
    """Socket伺服器連線對象設置，讀取config檔案，若失敗則用hardcode"""
    confp = configparser.ConfigParser()
    confp.read('resc-wifi.conf')
    try:   
        SOCKET_HOST = confp['wifi']['host']
    except:
        SOCKET_HOST = '192.168.4.1'

    try:
        SOCKET_PORT = int(confp['wifi']['port'])
    except:
        SOCKET_PORT = 8763

    global client_sock
    client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    global wifi_addr
    wifi_addr = (SOCKET_HOST,SOCKET_PORT)

def sock_recv_udp():
    """TODO Socket客戶端以udp接收"""
    while True:
        message_recv, addr = client_sock.recvfrom(1024)
        print(message_recv.decode())

def sock_write_udp():
    """TODO Socket客戶端以udp傳送"""
    while True:
        message_send = str(MessageFormat())
        client_sock.sendto(message_send.encode, wifi_addr)











def lora_setup():
    """LoRa 模組設置"""
    BOARD.setup()
    # parser = LoRaArgumentParser("Continuous LoRa receiver")

    """ TODO 此處先共用LoraRescuer"""
    global lora
    lora = LoraRescuer()

    # args = parser.parse_args(lora)

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

@unique
class TargetMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2





current_mode = TargetMode.LORA
if WIFI_SOCKET_TEST: current_mode = TargetMode.WIFI


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

    while current_mode == TargetMode.DUAL:
        pass

    while current_mode == TargetMode.WIFI:
        pass


if WIFI_SOCKET_TEST:
    print('socket setup')
    socket_setup()
    
    recv_udp_thread = threading.Thread(target=sock_recv_udp)
    write_udp_thread = threading.Thread(target=sock_write_udp)

    recv_udp_thread.start()
    write_udp_thread.start()

else: 
    lora_setup()

timer_thread = threading.Thread(target=timer)
timer_thread.setDaemon(True)




time.sleep(3)




try:
    main()
except KeyboardInterrupt as ke:
    sys.stderr.write(ke)
finally:
    if not WIFI_SOCKET_TEST:
        lora.set_mode(MODE.SLEEP)
        print(lora)
    BOARD.teardown()
