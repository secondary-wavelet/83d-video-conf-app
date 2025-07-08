import socket
import pickle
import cv2
import pyaudio
import time
import threading

class MediaSender:
    def __init__(self, target_ip: str, port: int = 5005):
        self.target_ip = target_ip
        self.port = port
        self.running = False
        self.thread = None

        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

        self.cap = cv2.VideoCapture(0)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def _send_loop(self):
        while self.running:
            timestamp = time.time()

            ret, frame = self.cap.read()
            if not ret:
                continue

            _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            video_bytes = encoded.tobytes()

            audio_bytes = self.audio_stream.read(1024)

            packet = {
                'timestamp': timestamp,
                'video': video_bytes,
                'audio': audio_bytes
            }

            data = pickle.dumps(packet)
            if len(data) <= 65507:
                self.sock.sendto(data, (self.target_ip, self.port))

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._send_loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.cap.release()
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        self.sock.close()
