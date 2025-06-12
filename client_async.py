import asyncio
import argparse

from netutils import Connection
from user import User

class Client:
    def __init__(self, ID: str):
        self.ID: str = ID
        self.user: User | None = None
        self.conn: Connection | None = None

    async def connect(self, server_ip: str, server_port: int):
        """Establishes a connection with the given IP"""

        self.conn = Connection(*await asyncio.open_connection(server_ip, server_port))        
        await self.conn._write_prefixed_str(self.ID)
        self.user = User(self.ID, self.conn)

    async def disconnect(self):
        await self.conn.close()

if __name__ == "__main__":
    async def main():
        client = Client(args.uid)
        await client.connect("localhost", 6969)
        print("Something happened!")
        await client.disconnect()
        
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("uid", help = "Your email address")
    args = parser.parse_args()

    asyncio.run(main())