# from client import Client

class ClientState:
    def __init__(self, ID):
        self.ID = ID
        self.is_sending_audio = False
        self.is_sending_video = False
    
        

class Room:
    """A Room is where a "call" takes place

    Handles call specific functions for each Client on the call, like audio and video streaming
    A Client can be in multiple Rooms at once. A Server can handle multiple Rooms at once
    """

    def __init__(self, room_ID):
        self.ID = room_ID
        self.clients: dict[str, ClientState] = {}
        print("room created")
    
    def add(self, clientID: str):
        self.clients[clientID] = ClientState(clientID)

    def remove(self, clientID: str):
        del self.clients[clientID]
        # handle sockets

    def toggle_audio(self, clientID: str):
        self.clients[clientID].is_sending_audio = not self.clients[clientID].is_sending_audio

    def toggle_video(self, clientID: str):
        self.clients[clientID].is_sending_video = not self.clients[clientID].is_sending_video