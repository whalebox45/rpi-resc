#Sample UDP Client - Multi threaded
#import the socket module
import socket
#import the threading module
import threading

# Define the message to the server
msgFromClient       = "Hello UDP Server"
bytesToSend         = str.encode(msgFromClient)
# Buffer size for receiving the datagrams from server
bufferSize          = 1024
# Server IP address and Port number
serverAddressPort   = ("127.0.0.1", 8080)
# Connect2Server forms the thread - for each connection made to the server
def Connect2Server():
    #Create a socket instance - A datagram socket
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send message to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)
    #Receive message from the server
    msgFromServer = UDPClientSocket.recvfrom(bufferSize)
    msg = "Message from Server {}".format(msgFromServer[0])
    print(msg)

print("Client - Main thread started")  
ThreadList  = []
ThreadCount = 20
# Create as many connections as defined by ThreadCount
for index in range(ThreadCount):
    ThreadInstance = threading.Thread(target=Connect2Server())
    ThreadList.append(ThreadInstance)
    ThreadInstance.start()

# Main thread to wait till all connection threads are complete
for index in range(ThreadCount):
    ThreadList[index].join()
