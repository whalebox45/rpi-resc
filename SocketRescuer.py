import socket
import time

class SocketRescuer(socket.socket):

    rx_data = ''

    sock_client_list = []

    def __init__(self, address):
        super.__init__(socket.AF_INET, socket.SOCK_DGRAM)
        super.bind(address)
    
    def recv_udp(self):
        while True:
            self.rx_data, addr = self.recvfrom(1024)
            if addr not in self.sock_client_list:
                self.sock_client_list.append(addr)
    
    def write_udp(self):
        message_send = str(self.rx_data)
        for addr in self.sock_client_list:
            self.sendto(message_send.encode(), addr)
        time.sleep(1)
