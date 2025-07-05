from protocol.msg_metadata import MsgType, MsgCategory

def invite_to_call(caller: str, callees: tuple[str], room: int) -> dict:
    return {
        "type": MsgType.CALL_BROADCAST,
        "category": MsgCategory.broadcast,
        "caller": caller,
        "callees": callees,
        "room": room
    }

def notify_toggled_audio() -> dict:
    return {

    }