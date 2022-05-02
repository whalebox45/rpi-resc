import socket, threading
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)
args = parser.parse_args()
if args.address: HOST = args.address
else: HOST = '127.0.0.1'

PORT = 7976



server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# server_sock.settimeout(3)
server_sock.bind((HOST, PORT))



clients_list = []

def recv_udp():
    while True:
        message_recv, addr = server_sock.recvfrom(1024)
        
        if addr not in clients_list:
            clients_list.append(addr)

        for addr in clients_list:
            server_sock.sendto(message_recv.decode(), addr)

        print(message_recv.decode())


def write_udp():
    while True:
        pass


recv_udp_thread = threading.Thread(target=recv_udp)

try:
    recv_udp_thread.start()
    while True:
        pass

except Exception as e:
    print(str(e))
    exit(1)
