from protocol.msg_metadata import MsgType, MsgCategory

def placed_call_ack(sent: list[str], failed: list[str], room: int) -> dict:
    return {
        "type": MsgType.CALL_ACK,
        "category": MsgCategory.response,
        "sent": sent,
        "failed": failed,
        "room": room
    }

def online_list(online: list[str]) -> dict:
    return {
        "type": MsgType.ONLINE_USERS_RESPONSE,
        "category": MsgCategory.response,
        "online": online
    }



def resp_toggle_audio() -> dict:
    return {

    }
