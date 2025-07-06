import socket
import pickle
import cv2
import pyaudio
import time


SERVER_IP = '127.0.0.1'
PORT = 5005
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
MAX_PACKET_SIZE = 65507  


audio = pyaudio.PyAudio()
audio_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                          input=True, frames_per_buffer=CHUNK)
cap = cv2.VideoCapture(0)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    while True:
        timestamp = time.time()

        
        ret, frame = cap.read()
        if not ret:
            continue
        _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 40])
        video_bytes = encoded.tobytes()

        
        cv2.imshow("Sending Video", frame)
        if cv2.waitKey(1) == ord('q'):
            break

       
        audio_bytes = audio_stream.read(CHUNK)

        
        packet = {
            'timestamp': timestamp,
            'video': video_bytes,
            'audio': audio_bytes
        }
        data = pickle.dumps(packet)

        if len(data) > MAX_PACKET_SIZE:
            print("⚠️ Packet too large! Skipping...")
            continue

        sock.sendto(data, (SERVER_IP, PORT))

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    audio_stream.stop_stream()
    audio_stream.close()
    audio.terminate()
    cv2.destroyAllWindows()
