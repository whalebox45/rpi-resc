import socket, threading, argparse


parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)
args = parser.parse_args()
if args.address: HOST = args.address
else: HOST = '127.0.0.1'

PORT = 7976

server_addr = (HOST, PORT)

# nickname = input("Choose your nickname: ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client_sock.connect((HOST, PORT))


def write_udp():
    while True:
        message_send = input()
        if message_send == 'exit':
            return
        client_sock.sendto(message_send.encode(), server_addr)

def recv_udp():
    while True:
        message_recv, addr = client_sock.recvfrom(1024)
        print(message_recv.decode())



recv_udp_thread = threading.Thread(target=recv_udp)
write_udp_thread = threading.Thread(target=write_udp)


try:
    recv_udp_thread.start()
    write_udp_thread.start()
    while True:
        pass

except Exception as e:
    print(str(e))
    exit(1)
