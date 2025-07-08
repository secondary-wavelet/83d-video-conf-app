import socket
import pickle
import threading
import time
from collections import defaultdict

class MediaRelayServer:
    def __init__(self, port=5005):
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", self.port))

        self.room_members = defaultdict(set)  # room_id -> set of (user_id, address)
        self.user_addresses = {}  # user_id -> (ip, port)

        self.running = False

    def start(self):
        print(f"[RelayServer] Listening on UDP port {self.port}...")
        self.running = True
        threading.Thread(target=self._listen_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.sock.close()

    def _listen_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65507)
                packet = pickle.loads(data)

                user_id = packet.get("user_id")
                room_id = packet.get("room_id")

                if not user_id or not room_id:
                    print("[RelayServer] Packet missing user_id or room_id, skipping...")
                    continue

                self.user_addresses[user_id] = addr
                self.room_members[room_id].add((user_id, addr))

                # Relay to everyone in the room *except* the sender
                for member_id, member_addr in self.room_members[room_id]:
                    if member_id != user_id:
                        try:
                            self.sock.sendto(data, member_addr)
                        except Exception as e:
                            print(f"[RelayServer] Failed to send to {member_id}@{member_addr}: {e}")

            except Exception as e:
                print("[RelayServer] Error in listen loop:", e)


if __name__ == "__main__":
    server = MediaRelayServer()
    server.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        server.stop()
