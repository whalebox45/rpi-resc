from enum import Enum
import socket

import configparser

config = configparser.ConfigParser()
config.read('wifi.conf')

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


socket_host = config.get('wifi','host',fallback='127.0.0.1')
socket_port = config.get('wifi','port',fallback='8763')

class WiFiActiveMode(Enum):
    sleep = 0
    active = 1