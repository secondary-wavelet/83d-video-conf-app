import asyncio
import argparse
from collections.abc import Iterator

from room import Room
from netutils import Connection

class Server:
    def __init__(self, IP, PORT):
        self.IP = IP
        self.PORT = PORT
        self.rooms: dict[int, Room] = {}
        self.client_map: dict[str, Connection] = {}

    def handle_request(self, req: dict) -> Iterator[tuple[Connection, dict]]:
        """Parses the given JSON, and returns pairs of (IP, Response)"""

        match req["type"]:        
            # case "REGISTER":

            
            case "CALL":
                for callee in req["callees"]:
                    yield self.client_map[callee], req

            case "RESPONSE":
                yield self.client_map[req["caller"]], req
                # add code for the actual call over here

            # case "CLOSE":


    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        conn = Connection(reader, writer)
        client_id = await conn._read_prefixed_str()
        self.client_map[client_id] = conn
        
        while True:
            req = await conn.read_prefixed_json()
            for target, response in self.handle_request(req):
                await target.write_prefixed_json(response)


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