import socket
import struct
import argparse

from room import Room

class Server:
    def __init__(self, IP: str, PORT: int):
        self.IP = IP
        self.PORT = PORT
        self.socket = None
        self.rooms: dict[int, Room] = {}
        self.client_map: dict[str, str] = {}
    
    def start(self):
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((self.IP, self.PORT))
            self.socket.listen()
            # print(f"Server listening on {self.IP}:{self.PORT}")
    
    def stop(self):
        if self.socket:
            self.socket.close()
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", default = "localhost", help = "Server IP Address")
    parser.add_argument("-p", "--port", type = int, default = 6969, help = "Server Port")

    args = parser.parse_args()
    s = Server(args.ip, args.port)
    s.start()