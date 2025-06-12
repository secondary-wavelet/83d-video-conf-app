import socket
import struct
import argparse

class Client:
    def __init__(self, ID: str):
        self.ID = ID
        self.socket = None

    def connect(self, server_ip: str, server_port: int):
        """Establishes a connection with the given IP"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((server_ip, server_port))
        self.socket.sendall(f"{self.ID}\n".encode())
        self.socket.recv

    def disconnect(self):
        self.socket.close()

    def place_call(self, otherID):
        pass

    def accept_call():
        pass
    
    def reject_call():
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("uid", help = "Your email address")

    args = parser.parse_args()

    client = Client(args.uid)
    client.connect("localhost", 6969)
    client.disconnect()