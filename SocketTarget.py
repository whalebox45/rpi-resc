import socket
import time

class SocketTarget:

    rx_data = ''
    tx_data = 'test'

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.socket.bind(address)
        self.addr = (host,int(port))

    def recv_udp(self):
        while True:
            msg, addr = self.socket.recvfrom(1024)
            self.rx_data = msg.decode()
            print("Socket RX:%s" % self.rx_data)
    
    def write_udp(self,message):
        self.tx_data = message
        message_send = str(self.tx_data)
        
        self.socket.sendto(message_send.encode(), self.addr)
        print("Socket TX:%s" % message_send)
        
        time.sleep(1)
        