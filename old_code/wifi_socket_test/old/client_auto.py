
import socket, threading, argparse
from time import sleep
nickname = input("Choose your nickname: ")

parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)

args = parser.parse_args()
if args.address:
    host = args.address
else: host = '127.0.0.1'

port = 7976


client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('ascii')
            if message == 'NICKNAME':
                client.send(nickname.encode('ascii'))
            else:
                print(message)
        except:
            print("An error occured!")
            client.close()
            break
def write():
    count = 0
    while True:
        try:
            message = '{}: {}'.format(nickname, count)
            client.send(message.encode('ascii'))
            count += 1
            sleep(1)
        except:
            print("An error occured!")
            client.close()
            break

receive_thread = threading.Thread(target=receive)
receive_thread.start()
write_thread = threading.Thread(target=write)
write_thread.start()

