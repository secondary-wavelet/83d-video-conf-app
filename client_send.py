import socket
import pickle
import cv2
import pyaudio
import time


SERVER_IP = '127.0.0.1'
PORT = 5000
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                          input=True, frames_per_buffer=CHUNK)


cap = cv2.VideoCapture(0)


sender_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sender_socket.connect((SERVER_IP, PORT))

try:
    while True:
        timestamp = time.time()

        
        ret, frame = cap.read()
        if not ret:
            continue
        _, encoded_frame = cv2.imencode('.jpg', frame)
        frame_bytes = encoded_frame.tobytes()

        
        audio_chunk = audio_stream.read(CHUNK)

        
        packet = {
            'timestamp': timestamp,
            'video': frame_bytes,
            'audio': audio_chunk
        }

        
        data = pickle.dumps(packet)
        sender_socket.sendall(len(data).to_bytes(4, 'big') + data)

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    sender_socket.close()
    audio_stream.stop_stream()
    audio_stream.close()
    audio.terminate()
