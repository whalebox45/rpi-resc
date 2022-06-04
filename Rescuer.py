

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

from SocketRescuer import SocketRescuer

argp = argparse.ArgumentParser()
argp.add_argument("-w","--wifi",action="store_true")
args = argp.parse_args()

WIFI_SOCKET_TEST = False
if args.wifi: WIFI_SOCKET_TEST = True





sock_client_list = []

def socket_new_setup():
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

    global sock_resc
    sock_resc = SocketRescuer((SOCKET_HOST,SOCKET_PORT))
    print("socket start")
    print(sock_resc)
    










'''

def socket_setup():
    """Socket伺服器設置，讀取config檔案，若失敗則用hardcode"""
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

    
    global server_sock
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind((SOCKET_HOST,SOCKET_PORT))
    print("socket start")
    print(server_sock)

def sock_recv_udp():
    while True:
        message_recv, addr = server_sock.recvfrom(1024)

        if addr not in sock_client_list:
            sock_client_list.append(addr)
        
        for addr in sock_client_list:
            server_sock.sendto(message_recv, addr)
        
        print("Socket RX: %s" % message_recv.decode())

def sock_write_udp():
    while True:
        message_send = str(MessageFormat())
        for addr in sock_client_list:
            server_sock.sendto(message_send.encode(), addr)
        time.sleep(1)


'''



def lora_setup():
    """LoRa 模組設置"""
    BOARD.setup()
    # parser = LoRaArgumentParser("Continuous LoRa receiver.")

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
    # lora.reset_ptr_rx()   
    lora.set_dio_mapping([0,0,0,0,0,0])
    lora.set_mode(MODE.RXCONT)

    # Sleep
    # lora.set_mode(MODE.SLEEP)
    time.sleep(5)

def lora_tx(lora:LoraRescuer,message:str):
    """將LoRa設為MODE.TX，並且以message參數傳入訊息內容"""
    lora.tx_data = message
    lora.set_mode(MODE.STDBY)
    lora.set_dio_mapping([1,0,0,0,0,0])
    lora.set_mode(MODE.TX)

    time.sleep(5)
    
    # lora.set_mode(MODE.SLEEP)
    # lora.reset_ptr_rx()

def lora_sleep(lora:LoraRescuer):
    lora.set_mode(MODE.SLEEP)

@unique
class RescuerMode(Enum):
    LORA = 0
    DUAL = 1
    WIFI = 2


current_mode = RescuerMode.LORA
if WIFI_SOCKET_TEST: current_mode = RescuerMode.WIFI




current_time = datetime.datetime.now()

rx_ok_count = 0
rx_fail_count = 0


            



def main():
    global current_mode, rx_ok_count, current_time
    stored_msg = object()



    while current_mode == RescuerMode.LORA:
        lora_rx(lora)
        '''
            如果在規定時間內收到LoRa訊息，增加計數器數值，並且發送自身的LoRa訊息
        '''

        fetched_time = current_time
        try:
            rd = lora.rx_data
            jrx = json.loads(rd.replace("\'", "\""))
            ser = jrx['MessageID']
            print(f'messageid: {ser}')
        except json.JSONDecodeError as jse:
            jrx = stored_msg
        except Exception as e:
            jrx = stored_msg
        

        if stored_msg != jrx:
        # if get_message_in10sec:
            stored_msg = jrx
            rx_ok_count += 1
            print(f'rx_ok_count: {rx_ok_count}')
            lora_tx(lora,str(MessageFormat()))

        '''
            TODO 如果在規定時間內都沒有收到LoRa訊息，就重設計數器數值
        '''
        
        # if lost_message_in10sec:
        #     rx_ok_count = 0
        
        '''
            TODO 如果計數器數值數值足夠大就切換至 DUAL 模式
            暫時設為 WIFI 模式
        '''
        if rx_ok_count >= 5:
            current_mode = RescuerMode.WIFI
            print('Change to WIFI Mode')
            rx_ok_count = 0
    




    while current_mode == RescuerMode.DUAL:
        fetched_time = current_time
        pass



    while current_mode == RescuerMode.WIFI:
        lora_sleep(lora)
        fetched_time = current_time
        try:
            rd = sock_resc.rx_data.decode()
            print(rd)
            jrx = json.loads(rd.replace("\'", "\""))
            ser = jrx['MessageID']
            print(f'messageid: {ser}')
        except json.JSONDecodeError as jse:
            jrx = stored_msg
            pass
        except Exception as e:
            jrx = stored_msg
            pass

        if stored_msg != jrx:
            stored_msg = jrx
            rx_ok_count += 1
            print(f'rx_ok_count: {rx_ok_count}')
            sock_resc.write_udp(str(MessageFormat()))

        if stored_msg == jrx:
            pass

        """
        TODO 測試用：WIFI模式五次成功時返回LORA
        """
        if rx_ok_count >= 5:
            current_mode = RescuerMode.LORA
            print('change')


print('socket setup')
# socket_setup()
# recv_udp_thread = threading.Thread(target=sock_recv_udp())
# write_udp_thread = threading.Thread(target=sock_write_udp())
socket_new_setup()

recv_udp_thread = threading.Thread(target=sock_resc.recv_udp)
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
