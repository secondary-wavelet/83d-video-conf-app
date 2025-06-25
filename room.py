from client import Client

class Room:
    """A Room is where a "call" takes place

    Handles call specific functions for each Client on the call, like audio and video streaming
    A Client can be in multiple Rooms at once. A Server can handle multiple Rooms at once
    """

    def __init__(self, clients: set[Client] | None = set()):
        self.clients = clients
    
    def add(self, client: Client):
        self.clients.add(client)
        # handle sockets

    def remove(self, client: Client):
        if client in self.clients:
            self.clients.remove(client)
        # handle sockets

    def toggle_audio(self, client: Client):
        pass

    def toggle_video(self, client: Client):
        pass