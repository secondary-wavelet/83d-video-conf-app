from client import Client

class Room:
    """A Room is where a "call" takes place

    Handles call specific functions for each Client on the call, like audio and video streaming
    A Client can be in multiple Rooms at once. A Server can handle multiple Rooms at once
    """

    def __init__(self, clients: list[Client] | None = set()):
        self.clients = clients