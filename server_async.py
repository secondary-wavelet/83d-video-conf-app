import asyncio
import argparse
from collections.abc import Iterator

from room import Room
from netutils import Connection

class Server:
    def __init__(self, IP: str, PORT: int):
        self.IP = IP
        self.PORT = PORT
        self.rooms: dict[int, Room] = {}
        self.client_map: dict[str, Connection] = {}

    # async def handle_call_request(callees = list[str], caller = str, )

    async def handle_request(self, req: dict, sender_conn: Connection) -> None:
        """Parses the given JSON, and calls the required functions"""

        match req["type"]:                    
            case "CALL":
                sent, failed = [], []    
                for callee in req["callees"]:
                    if callee in self.client_map:
                        sent.append(callee)
                        await self.client_map[callee].write_prefixed_json(req)
                    else:
                        failed.append(callee)
                await sender_conn.write_prefixed_json({
                    "type": "CALL_ACK",
                    "sent": sent,
                    "failed": failed
                })
                

            case "RESPONSE":
                yield self.client_map[req["caller"]], req
                # add code for the actual call over here

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