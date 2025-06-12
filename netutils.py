import socket
import asyncio
import struct
import json

def recvall(socket: socket.socket, n: int) -> bytes:
    msg = bytearray()
    while len(msg) < n:
        packet = socket.recv(n - len(msg))
        if not packet:
            raise ConnectionError(f"Socket connection broken: Expected {n} bytes, recieved {len(msg)}")
        msg.extend(packet)

    return bytes(msg)



class Connection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

    async def _read_int32(self) -> int:
        n = await self.reader.readexactly(4)
        return struct.unpack("!i", n)[0]

    async def _read_prefixed_str(self) -> str:
        msglen: int = await self._read_int32()
        msg = await self.reader.readexactly(msglen)
        return msg.decode()

    async def read_prefixed_json(self) -> dict:
        req = await self._read_prefixed_str()
        return json.loads(req)
    
    async def _write_prefixed_str(self, msg: str):
        bytestr = msg.encode()
        prefix = struct.pack("!i", len(bytestr))
        msg = prefix + bytestr
        self.writer.write(msg)
        await self.writer.drain()
    
    async def write_prefixed_json(self, req: dict):
        json_str = json.dumps(req).encode()
        prefix = struct.pack("!i", len(json_str))
        msg = prefix + json_str
        self.writer.write(msg)
        await self.writer.drain()
    
    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()