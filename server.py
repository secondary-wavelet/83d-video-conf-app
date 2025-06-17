import socket
import threading
from config import HOST, VIDEO_PORT, AUDIO_PORT

def handle_pipe(client1, client2, label):
    while True:
        try:
            data = client1.recv(4096)
            if not data:
                break
            client2.sendall(data)
        except:
            break
    client1.close()
    client2.close()
    print(f"[{label}] Connection closed.")

def start_server(port, label):
    server = socket.socket()
    server.bind((HOST, port))
    server.listen(2)
    print(f"[{label}] Waiting for sender and receiver on port {port}...")
    c1, _ = server.accept()
    print(f"[{label}] Sender connected.")
    c2, _ = server.accept()
    print(f"[{label}] Receiver connected.")
    threading.Thread(target=handle_pipe, args=(c1, c2, f"{label} → forward")).start()
    threading.Thread(target=handle_pipe, args=(c2, c1, f"{label} ← backward")).start()

threading.Thread(target=start_server, args=(VIDEO_PORT, "Video")).start()
threading.Thread(target=start_server, args=(AUDIO_PORT, "Audio")).start()
