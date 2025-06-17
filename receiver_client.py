import socket
import threading
import cv2
import pyaudio
import numpy as np
from config import HOST, VIDEO_PORT, AUDIO_PORT, CHUNK_SIZE

def video_receiver():
    sock = socket.socket()
    sock.connect((HOST, VIDEO_PORT))
    try:
        while True:
            size_data = sock.recv(4)
            if not size_data:
                break
            size = int.from_bytes(size_data, 'big')
            data = b''
            while len(data) < size:
                packet = sock.recv(size - len(data))
                if not packet:
                    break
                data += packet
            frame = cv2.imdecode(np.frombuffer(data, np.uint8), 1)
            if frame is not None:
                cv2.imshow("Video from Sender", frame)
                if cv2.waitKey(1) == ord('q'):
                    break
    finally:
        sock.close()
        cv2.destroyAllWindows()

def audio_receiver():
    p = pyaudio.PyAudio()
    sock = socket.socket()
    sock.connect((HOST, AUDIO_PORT))

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, output=True, frames_per_buffer=CHUNK_SIZE)
    try:
        while True:
            data = sock.recv(CHUNK_SIZE)
            if not data:
                break
            stream.write(data)
    finally:
        stream.stop_stream()
        stream.close()
        sock.close()
        p.terminate()

threading.Thread(target=video_receiver).start()
threading.Thread(target=audio_receiver).start()
