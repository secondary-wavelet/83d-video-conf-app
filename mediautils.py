from media_sender import MediaSender
from media_receiver import MediaReceiver

class MediaConnection:
    def __init__(self, server_ip, user_id, room_id, video_label=None):
        self.sender = MediaSender(server_ip=server_ip, user_id=user_id, room_id=room_id)
        self.receiver = MediaReceiver(video_label=video_label)

    def start(self):
        self.sender.start()
        self.receiver.start()

    def stop(self):
        self.sender.stop()
        self.receiver.stop()
