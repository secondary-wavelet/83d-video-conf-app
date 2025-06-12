from netutils import Connection
from functools import wraps

def sends_request(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        req = func(self, *args, **kwargs)
        await self.conn.write_prefixed_json(req)
    return wrapper

class User:
    def __init__(self, ID: str, conn: Connection):
        self.ID = ID
        self.conn = conn

    # @sends_request
    # async def register(self):
    #     return {
    #         "type": "REGISTER",
    #         "id": self.ID
    #     }
    
    @sends_request
    async def place_call(self, *callees: tuple[str]) -> dict:
        return {
            "type": "CALL",
            "caller": self.ID,
            "callees": callees
        }
    
    @sends_request
    async def respond_to_call(self, caller: str, accepted: bool) -> dict:
        return {
            "type": "RESPONSE",
            "callee": self.ID,
            "caller": caller,
            "accepted": accepted
        }