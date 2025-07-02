import socket
import pickle
import cv2
import pyaudio
import numpy as np
import time
from queue import PriorityQueue

SERVER_IP = '127.0.0.1'
PORT = 5001  
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BUFFER_DELAY = 0.1  


audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                          output=True, frames_per_buffer=CHUNK)


receiver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
receiver_socket.connect((SERVER_IP, PORT))


sync_buffer = PriorityQueue()

def receive_stream():
    while True:
        try:
            length_data = receiver_socket.recv(4)
            if not length_data:
                continue
            length = int.from_bytes(length_data, 'big')

            data = b''
            while len(data) < length:
                more = receiver_socket.recv(length - len(data))
                if not more:
                    break
                data += more

            if not data:
                continue

            packet = pickle.loads(data)
            sync_buffer.put((packet['timestamp'], packet))

        except Exception as e:
            print("Error:", e)
            break

def playback_loop():
    while True:
        if sync_buffer.empty():
            time.sleep(0.01)
            continue

        timestamp, packet = sync_buffer.queue[0]
        now = time.time()
        if now - timestamp >= BUFFER_DELAY:
            _, packet = sync_buffer.get()

            
            frame_data = packet['video']
            frame = cv2.imdecode(np.frombuffer(frame_data, np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow('Received Video', frame)
            if cv2.waitKey(1) == ord('q'):
                break

            
            audio_stream.write(packet['audio'])

        else:
            time.sleep(0.005)

import threading
threading.Thread(target=receive_stream, daemon=True).start()
threading.Thread(target=playback_loop, daemon=True).start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

receiver_socket.close()
cv2.destroyAllWindows()
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
