import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.settimeout(3)

