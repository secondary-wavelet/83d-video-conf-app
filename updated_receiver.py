import socket
import pickle
import cv2
import numpy as np
import pyaudio
import time
from queue import PriorityQueue
import threading


PORT = 5005
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
BUFFER_DELAY = 0.1  


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', PORT))
sock.setblocking(False)

audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                          output=True, frames_per_buffer=CHUNK)

sync_buffer = PriorityQueue()

def receive_loop():
    while True:
        try:
            data, _ = sock.recvfrom(65507)
            packet = pickle.loads(data)
            sync_buffer.put((packet['timestamp'], packet))
        except:
            time.sleep(0.005)

def playback_loop():
    while True:
        if sync_buffer.empty():
            time.sleep(0.01)
            continue

        ts, pkt = sync_buffer.queue[0]
        now = time.time()
        if now - ts >= BUFFER_DELAY:
            _, pkt = sync_buffer.get()

            
            frame = cv2.imdecode(np.frombuffer(pkt['video'], np.uint8), cv2.IMREAD_COLOR)
            cv2.imshow("Received Video", frame)
            if cv2.waitKey(1) == ord('q'):
                break

            
            audio_stream.write(pkt['audio'])
        else:
            time.sleep(0.005)


threading.Thread(target=receive_loop, daemon=True).start()
threading.Thread(target=playback_loop, daemon=True).start()


try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    pass

cv2.destroyAllWindows()
audio_stream.stop_stream()
audio_stream.close()
audio.terminate()
