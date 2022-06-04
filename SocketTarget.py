import socket
import time

class SocketTarget:

    rx_data = ''
    tx_data = 'test'

    def __init__(self, address):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(address)
        self.addr = address

    def recv_udp(self):
        while True:
            self.rx_data, addr = self.socket.recvfrom(1024)
    
    def write_udp(self,message):
        self.tx_data = message
        message_send = str(self.tx_data)
        self.socket.sendto(message_send.encode(), self.addr)
        time.sleep(1)
        