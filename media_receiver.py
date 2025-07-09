import socket
import pickle
import cv2
import numpy as np
import pyaudio
import time
import threading
from queue import PriorityQueue
from PIL import Image, ImageTk


class MediaReceiver:
    def __init__(self, listen_port=5005, buffer_delay=0.1, video_label=None):
        self.listen_port = listen_port
        self.buffer_delay = buffer_delay
        self.video_label = video_label  # <-- Store Tkinter label
        self.tk_img = None  # <-- Keep reference to PhotoImage

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("", listen_port))
        self.sock.setblocking(False)

        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=44100,
            output=True,
            frames_per_buffer=1024
        )

        self.sync_buffer = PriorityQueue()
        self.running = False
        self.receive_thread = None
        self.playback_thread = None

    def start(self):
        self.running = True
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.playback_thread = threading.Thread(target=self._playback_loop, daemon=True)
        self.receive_thread.start()
        self.playback_thread.start()

    def set_display_callback(self, callback):
        self.tk_callback = callback

    def stop(self):
        self.running = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1)
        if self.playback_thread:
            self.playback_thread.join(timeout=1)
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        self.sock.close()
        cv2.destroyAllWindows()

    def _receive_loop(self):
        while self.running:
            try:
                data, _ = self.sock.recvfrom(65507)
                packet = pickle.loads(data)
                self.sync_buffer.put((packet['timestamp'], packet))
            except BlockingIOError:
                time.sleep(0.005)

    def _playback_loop(self):
        while self.running:
            if self.sync_buffer.empty():
                time.sleep(0.01)
                continue

            ts, pkt = self.sync_buffer.queue[0]
            now = time.time()
            if now - ts >= self.buffer_delay:
                _, pkt = self.sync_buffer.get()

                # Decode video frame
                frame = cv2.imdecode(np.frombuffer(pkt['video'], np.uint8), cv2.IMREAD_COLOR)
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame_rgb)
                tk_img = ImageTk.PhotoImage(img)

                # Display video in Tkinter
                if self.video_label:
                    self.video_label.after(0, self._update_label_image, tk_img)

                # Play audio
                self.audio_stream.write(pkt['audio'])
            else:
                time.sleep(0.005)

    def _update_label_image(self, tk_img):
        self.tk_img = tk_img  # prevent garbage collection
        self.video_label.config(image=self.tk_img)
