import socket, threading, argparse


parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)
args = parser.parse_args()
if args.address: HOST = args.address
else: HOST = '127.0.0.1'

PORT = 7976

server_addr = (HOST, PORT)

nickname = input("Choose your nickname: ")

client_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# client_sock.connect((HOST, PORT))


def write_udp():
    while True:
        message_send = input()
        if message_send == 'exit':
            break
        client_sock.sendto(message_send.encode(), server_addr)

def recv_udp():
    while True:
        message_recv, addr = client_sock.recvfrom(1024)
        print(message_recv.decode())




# receive_thread = threading.Thread(target=receive)
# receive_thread.setDaemon(True)
# write_thread = threading.Thread(target=write)
# write_thread.setDaemon(True)


try:
    # receive_thread.start()
    # write_thread.start()
    while True:
        pass

except Exception as e:
    print(str(e))
    # client_sock.send('{}:Disconnect from {}'.format(client_sock.getsockname(),str(e))).encode()
    # client_sock.send(bytes('except'))
    # client_sock.close()
    exit(1)
