import socket
import threading
from time import sleep

HOST = '127.0.0.1'
PORT = 7976

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.settimeout(3)
server.bind((HOST, PORT))
server.listen()

conn_list = []

def handle(client):
    while True:
        try:
            message = client.recv(1024)
            print(message.decode('utf-8'))
        except:
            conn_list.remove(client)
            client.close()
            break


def receive():
    while True:
        try:
            conn, address = server.accept()
            print("Connected with {}".format(str(address)))
            
            conn_list.append(conn)

            handle_thread = threading.Thread(target=handle, args=(conn,))
            handle_thread.start()



        except socket.timeout as se:
            pass

        except Exception as e:
            pass


def write():
    count = 0
    while True:
        try:
            message = 'server: {}'.format(count)
            for x in conn_list:
                x.send(message.encode('utf-8'))
            sleep(1)
            count+=1
        except Exception as e:
            pass

receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()