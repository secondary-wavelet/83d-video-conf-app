import socket
import pickle
import cv2
import pyaudio
import time
import threading


class MediaSender:
    def __init__(self, server_ip, server_port=5005, user_id=None, room_id=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            input=True,
            frames_per_buffer=1024
        )

        self.cap = cv2.VideoCapture(0)
        self.running = False
        self.send_thread = None

        self.user_id = user_id
        self.room_id = room_id

    def start(self):
        self.running = True
        self.send_thread = threading.Thread(target=self._send_loop, daemon=True)
        self.send_thread.start()

    def stop(self):
        self.running = False
        if self.send_thread:
            self.send_thread.join(timeout=1)
        self.cap.release()
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        self.sock.close()
        cv2.destroyAllWindows()

    def _send_loop(self):
        while self.running:
            timestamp = time.time()

            ret, frame = self.cap.read()
            if not ret:
                continue
            _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
            video_bytes = encoded.tobytes()

            cv2.imshow("Sending Video", frame)
            if cv2.waitKey(1) == ord('q'):
                self.stop()
                break

            audio_bytes = self.audio_stream.read(1024)

            packet = {
                'timestamp': timestamp,
                'user_id': self.user_id,
                'room_id': self.room_id,
                'video': video_bytes,
                'audio': audio_bytes
            }
            data = pickle.dumps(packet)

            if len(data) <= 65507:
                self.sock.sendto(data, (self.server_ip, self.server_port))
