from socket import socket, AF_INET, SOCK_DGRAM
import sys

def ask():
    host = '127.0.0.1'
    port = 123
    address = (host, port)
    with socket(AF_INET, SOCK_DGRAM) as _socket:
        message = get_request()
        _socket.sendto(message, address)
        _socket.settimeout(5)
        response, recv_address = _socket.recvfrom(1024)
        if address == recv_address:
            print(response)

def get_request():
    return 0b00100011.to_bytes(1, "big") + bytes(47)

if __name__ == "__main__":
    ask()