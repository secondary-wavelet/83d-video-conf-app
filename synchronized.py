import cv2
import pyaudio
import threading
import numpy as np

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


p = pyaudio.PyAudio()

audio_input = p.open(format=FORMAT,
                     channels=CHANNELS,
                     rate=RATE,
                     input=True,
                     frames_per_buffer=CHUNK)

audio_output = p.open(format=FORMAT,
                      channels=CHANNELS,
                      rate=RATE,
                      output=True,
                      frames_per_buffer=CHUNK)

running = True

def capture_audio():
    while running:
        try:
            data = audio_input.read(CHUNK, exception_on_overflow=False)
            audio_output.write(data)
        except Exception as e:
            print("Audio error:", e)
            break

def capture_video():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    while running:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        cv2.imshow("Video Feed", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

audio_thread = threading.Thread(target=capture_audio)
video_thread = threading.Thread(target=capture_video)

audio_thread.start()
video_thread.start()

video_thread.join()

running = False
audio_thread.join()
audio_input.stop_stream()
audio_input.close()
audio_output.stop_stream()
audio_output.close()
p.terminate()
