from concurrent.futures.process import _ThreadWakeup
import socket, threading
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)
args = parser.parse_args()
if args.address: HOST = args.address
else: HOST = '127.0.0.1'

PORT = 7976



server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.settimeout(3)
server.bind((HOST, PORT))
server.listen()


clients = []


def broadcast(message):
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            message_str = message.decode('utf-8')
            if message_str == '{}:Disconnect'.format(client)):
                raise Exception
            print(message_str)

            broadcast(message_str)
        except Exception as e:
            print('{} is Disconnected'.format(client))
            clients.remove(client)
            client.close()
            return


def receive():
    while True:
        try:
            client, address = server.accept()
            print("Connected with {},{}".format(str(client),str(address)))
            clients.append(client)

            client.send('Connected to server!'.encode('ascii'))

            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

        except socket.timeout as se:
            pass

        except Exception as e:
            print(str(e))
            server.close()
            return

def write():
    while True:
        try:
            message = input()
            broadcast(message.encode('utf-8'))
        except Exception as e:
            print(str(e))
            server.close()
            for c in clients:
                c.close()
            return

recv_thread = threading.Thread(target=receive)
recv_thread.setDaemon(True) 
write_thread = threading.Thread(target=write)
write_thread.setDaemon(True)

try:
    
    recv_thread.start()
    write_thread.start()
    while True:
        pass
except Exception as e:
    for c in clients:
        c.close()
