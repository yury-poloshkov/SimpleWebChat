#!/bin/python3
import socket
import threading

# Connection Data
host = '127.0.0.1'
port = 55555
encoding = 'utf-8'

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

# Lists For Clients and Their Nicknames
clients = []
nicknames = []

# Sending Messages To All Connected Clients
def broadcast(message):
    is_private = message.decode(encoding).find(': %')
    if is_private != -1:
        send_private(message)
    else:
        for client in clients:
            client.send(message)

# Sending Private Message to <%nickname> Client
def send_private(message):
    dec_message = message.decode(encoding)
    private_nick = dec_message.find(': %')
    receiver = dec_message[private_nick+3:dec_message.find(' ',private_nick+3)]
    dec_message = 'private from ' + dec_message[:private_nick + 1] + dec_message[dec_message.find(' ',private_nick+3):]
    client = clients[nicknames.index(receiver)]
    client.send(dec_message.encode(encoding))

# Handling Messages From Clients
def handle(client):
    while True:
        try:
            # Broadcasting Messages
            message = client.recv(1024)
            broadcast(message)
        except:
            # Removing And Closing Clients
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast('{} left!'.format(nickname).encode(encoding))
            nicknames.remove(nickname)
            break

# Receiving / Listening Function
def receive():
    while True:
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))

        # Request And Store Nickname
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode(encoding)
        nicknames.append(nickname)
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode(encoding))
        client.send('Connected to server!'.encode(encoding))

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print("Server if listening...")
receive()