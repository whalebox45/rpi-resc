import socket
import time

class SocketRescuer:

    rx_data = ''
    tx_data = 'test'

    sock_client_list = []

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
    
    def recv_udp(self):
        while True:
            self.rx_data, addr = self.socket.recvfrom(1024)
            print("Socket RX:%s" % self.rx_data)
            if addr not in self.sock_client_list:
                self.sock_client_list.append(addr)
            
    
    def write_udp(self,message):
        self.tx_data = message
        message_send = str(self.tx_data)
        for addr in self.sock_client_list:
            self.socket.sendto(message_send.encode(), addr)
        print("Socket TX:%s"%message_send)
        
        time.sleep(1)
