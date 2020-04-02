from enum import IntEnum


class Action(IntEnum):
    REQUEST = 1
    RANDOM = 2


class Message:
    def __init__(self, action: Action, data: str = "") -> None:
        self.action = action
        self.data = data

    def encode(self) -> bytes:
        return bytes((self.action,)) + self.data.encode()

    @staticmethod
    def decode(data: bytes) -> "Message":
        return Message(Action(data[0]), data[1:].decode())


def request(data: str) -> Message:
    return Message(Action.REQUEST, data)


def random() -> Message:
    return Message(Action.RANDOM)
