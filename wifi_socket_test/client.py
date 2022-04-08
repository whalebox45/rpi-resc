import socket, threading, argparse


parser = argparse.ArgumentParser()
parser.add_argument("-a","--address",dest='address',action="store",type=str)
args = parser.parse_args()
if args.address: HOST = args.address
else: HOST = '127.0.0.1'

PORT = 7976

nickname = input("Choose your nickname: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def receive():
    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            print(message)
        except (Exception,ConnectionResetError) as e:
            raise e
            print(str(e))
            client.close()
            return


def write():
    while True:
        try:
            message = '{}: {}'.format(nickname, input(''))
            client.send(message.encode('utf-8'))
        except Exception as e:
            raise e
            print(str(e))
            client.close()
            return


try:
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()
    write_thread = threading.Thread(target=write)
    write_thread.start()
except Exception as e:
    client.close()
    exit(1)
