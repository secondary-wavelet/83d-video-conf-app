import asyncio
import argparse
from collections.abc import Iterator

from room import Room
from netutils import Connection
from protocol import responses, broadcasts
from protocol.msg_metadata import MsgType

class Server:
    def __init__(self, IP: str, PORT: int):
        self.IP = IP
        self.PORT = PORT
        self.rooms: dict[int, Room] = {}
        self.client_map: dict[str, Connection] = {}
        self.rid_ctr = 0

    def get_rid(self):
        self.rid_ctr += 1
        return self.rid_ctr
    
    async def handle_request(self, req: dict, sender_conn: Connection) -> None:
        """Parses the given JSON, and calls the required functions"""

        print(f"req received: {req}")

        match req["type"]:                    
            case MsgType.CALL_REQUEST:
                print("received call request")
                rid = self.get_rid()
                self.rooms[rid] = Room(rid)
                self.rooms[rid].add(req["caller"])
                sent, failed = [], []
                for callee in req["callees"]:
                    if callee in self.client_map:
                        sent.append(callee)
                        await self.client_map[callee].write_prefixed_json(
                            broadcasts.invite_to_call(req["caller"], req["callees"], rid)
                        )
                    else:
                        failed.append(callee)
                await sender_conn.write_prefixed_json(responses.placed_call_ack(sent, failed))            
            
            case MsgType.CALL_REPLY:
                # callee = req["callee"]
                if req["is_accepted"]:
                    self.rooms[req["room"]].add(req["callee"])

            
            case MsgType.ONLINE_USERS_REQUEST:
                await sender_conn.write_prefixed_json(responses.online_list(self.client_map.keys))
            
            case MsgType.TOGGLE_AUDIO_REQUEST:
                room: int = req["room"]
                user = req["target"]
                self.rooms[room].toggle_audio(user)
                for client in self.rooms[room].clients:
                    await self.client_map[client].write_prefixed_json(
                        broadcasts.notify_toggled_audio() #write better
                    )
                

            case "TOGGLE_VIDEO":
                room = req["room"]
                user = req["target"]
                self.rooms[room].toggle_audio(user)
                # ADD CODE TO SEND AN ACK/BROADCAST
                
            # case "CLOSE":


    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        conn = Connection(reader, writer)
        client_id = await conn._read_prefixed_str()
        self.client_map[client_id] = conn
        print(f"Connected to {client_id}")
        while True:
            req = await conn.read_prefixed_json()
            await self.handle_request(req, conn)
            


    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.IP, self.PORT)
        print(f"Server running on {self.IP}:{self.PORT}")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", default = "localhost", help = "Server IP Address")
    parser.add_argument("-p", "--port", type = int, default = 6969, help = "Server Port")

    args = parser.parse_args()
    s = Server(args.ip, args.port)
    asyncio.run(s.start())  

    print(MsgType.CALL_ACK)