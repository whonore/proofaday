import socket
import sys
from argparse import ArgumentParser, FileType
from typing import Optional, Tuple


import proofaday.constants as consts
import proofaday.message as message
from proofaday.message import Action, Message


class ProofServerError(Exception):
    pass


class ProofClient:
    retries = 10

    def __init__(self, port: int, timeout: float) -> None:
        self.port = port
        self.timeout = timeout

    def send(self, msg: Message) -> Tuple[bool, str]:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg.encode(), (consts.HOST, self.port))
            try:
                if msg.action in (Action.CHECK, Action.KILL):
                    sock.settimeout(0.1)
                    sock.recv(1)
                    return True, ""
                else:
                    sock.settimeout(self.timeout)
                    return True, sock.recv(4096).decode()
            except socket.timeout:
                return False, "Server timed out"

    def check(self) -> bool:
        return self.send(message.check())[0]

    def kill(self) -> bool:
        return self.send(message.kill())[0]

    def query(self, name: Optional[str]) -> str:
        if name is not None:
            return self.send(message.request(name))[1]
        return self.send(message.random())[1]


def main() -> None:
    parser = ArgumentParser(description="Fetch a random proof")
    parser.add_argument("name", nargs="?", default=None)
    parser.add_argument("-p", "--port", type=int, default=consts.PORT)
    parser.add_argument("-t", "--timeout", type=float, default=consts.CLIENT_TIMEOUT)
    parser.add_argument("-o", "--output", type=FileType("w"), default=sys.stdout)
    args = parser.parse_args()

    client = ProofClient(args.port, args.timeout)
    try:
        print(client.query(args.name), file=args.output)
    except ProofServerError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
