from protocol.msg_metadata import MsgType, MsgCategory

def register(user_ID: str) -> dict:
    return {
        "type": MsgType.REGISTER,
        "category": MsgCategory.request,
        "ID": user_ID
    }

def place_call(caller_ID: str, callees: tuple[str]) -> dict:
    return {
        "type": MsgType.CALL_REQUEST,
        "category": MsgCategory.request,
        "caller": caller_ID,
        "callees": callees
    }

def reply_to_call(responder_ID, caller: str, room: int, is_accepted: bool) -> dict:
    return {
        "type": MsgType.CALL_REPLY,
        "category": MsgCategory.request,
        "callee": responder_ID,
        "caller": caller,
        "is_accepted": is_accepted
    }

def get_online_list() -> dict:
    return {
        "type": MsgType.ONLINE_USERS_REQUEST,
        "category": MsgCategory.request
    }

def req_toggle_audio(room_ID: int) -> dict:
    return {
        "type": MsgType.TOGGLE_AUDIO_REQUEST,
        "category": MsgCategory.request,
        "room": room_ID,
        # "target": ID,
    }

def req_toggle_video(room_ID: int) -> dict:
    return {
        "type": MsgType.TOGGLE_VIDEO_REQUEST,
        "category": MsgCategory.request,
        "room": room_ID,
        # "target": ID,
    }

def leave_call(room_ID: int) -> dict:
    return {
        "type": MsgType.LEAVE_CALL_REQUEST,
        "category": MsgCategory.request,
        "room": room_ID
    }