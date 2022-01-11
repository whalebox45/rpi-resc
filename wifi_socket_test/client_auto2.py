import socket
import threading
from time import sleep

HOST = '127.0.0.1'
PORT = 7976

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except Exception as e:
            client.close()
            print(str(e))
            break

def write():
    count = 0
    while True:
        try:
            message = '{}'.format(count)
            client.send(message.encode('utf-8'))
            print(message)
            count += 1
            sleep(1)
        except Exception as e:
            client.close()
            print(str(e))
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()