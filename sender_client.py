import socket
import threading
import cv2
import pyaudio
from config import HOST, VIDEO_PORT, AUDIO_PORT, CHUNK_SIZE

def video_sender():
    sock = socket.socket()
    sock.connect((HOST, VIDEO_PORT))
    cap = cv2.VideoCapture(0)

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame = cv2.resize(frame, (320, 240))
            encoded = cv2.imencode('.jpg', frame)[1].tobytes()
            size = len(encoded).to_bytes(4, 'big')
            sock.sendall(size + encoded)
    except:
        pass
    finally:
        cap.release()
        sock.close()

def audio_sender():
    p = pyaudio.PyAudio()
    sock = socket.socket()
    sock.connect((HOST, AUDIO_PORT))

    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=CHUNK_SIZE)
    try:
        while True:
            data = stream.read(CHUNK_SIZE)
            sock.sendall(data)
    except:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        sock.close()
        p.terminate()

threading.Thread(target=video_sender).start()
threading.Thread(target=audio_sender).start()
