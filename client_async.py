import asyncio
import argparse

from netutils import Connection
from media_sender import MediaSender
from media_receiver import MediaReceiver
from protocol import requests
from protocol.msg_metadata import MsgCategory, MsgType


class Client:
    def __init__(self, ID: str):
        self.ID: str = ID
        self.conn: Connection | None = None
        self.lock = asyncio.Lock()
        self.response_queue = asyncio.Queue()
        self.media_sender = None
        self.media_receiver = None

        self.on_incoming_call = None
        self.on_call_ended = None
        self.schedule_callback = None  # NEW: a function like root.after
    
    def set_event_handlers(self, *, on_incoming_call=None, on_call_ended=None, on_placing_call=None, scheduler=None):
        self.on_incoming_call = on_incoming_call
        self.on_call_ended = on_call_ended
        # self.on_placing_call = on_placing_call
        self.schedule_callback = scheduler
        
    def set_broadcast_handler(self, handler_fn):
        self.broadcast_handler = handler_fn

    def start_media_stream(self, room_id):
        self.media_sender = MediaSender(server_ip=self.server_ip, room_id=room_id, user_id=self.user_id)
        self.media_receiver = MediaReceiver()  # optionally: choose a port
        self.media_sender.start()
        self.media_receiver.start()

    def stop_media_stream(self):
        if self.media_sender:
            self.media_sender.stop()
        if self.media_receiver:
            self.media_receiver.stop()

    async def connect(self, server_ip: str, server_port: int):
        """Establishes a connection with the given IP"""

        self.conn = Connection(*await asyncio.open_connection(server_ip, server_port))        
        await self.conn._write_prefixed_str(self.ID)

    async def _send(self, req: dict):
        if self.conn:
            await self.conn.write_prefixed_json(req)
        else:
            print("[Client] Tried to send, but not connected!")

    def handle_broadcast(self, msg):
        match msg["type"]:
            case MsgType.CALL_BROADCAST:
                if self.on_incoming_call:
                    if self.schedule_callback:
                        self.schedule_callback(0, self.on_incoming_call, msg["caller"])
                    else:
                        self.on_incoming_call(msg["caller"])
    
    async def listen(self):
        while True:
            msg = await self.conn.read_prefixed_json()
            print(msg)
            if msg["category"] == MsgCategory.response:
                await self.response_queue.put(msg)
            else:
                self.handle_broadcast(msg)
    
    async def send_and_recv(self, req: dict):
        async with self.lock:
            await self.conn.write_prefixed_json(req)
            return await self.response_queue.get()

    async def disconnect(self):
        await self.conn.close()


    async def place_call(self, *callees: str):
        req = requests.place_call(self.ID, callees)
        resp = await self.send_and_recv(req)
        if resp: return True
        else: return False

    async def respond_to_call(self, caller_ID, is_accepted):
        req = requests.respond_to_call(self.ID, caller_ID, is_accepted)
        resp = await self.send_and_recv(req)
        if is_accepted:
            media_ip = resp.get('media_ip', '127.0.0.1')
            media_port = resp.get('media_port', 5005)

            self.media_sender = MediaSender(media_ip, media_port)
            self.media_sender.start()      
    
    # async def end_call():
    #     if self.media_sender:
    #         self.media_sender.stop()
    #         self.media_sender = None


    async def req_online_list(self):
        req = requests.req_online_list()
        resp = await self.send_and_recv
    
    


if __name__ == "__main__":
    async def main():
        client = Client(args.uid)
        await client.connect("localhost", 6969)
        print("Something happened!")
        input()
        await client.disconnect()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("uid", help = "Your email address")
    args = parser.parse_args()

    asyncio.run(main())