import socket
import sys
from argparse import ArgumentParser, FileType
from pathlib import Path
from typing import Optional


import proofaday.constants as consts
import proofaday.message as message
from proofaday.message import Message
from proofaday.status import Status


class ClientError(Exception):
    pass


class ProofClient:
    retries = 10

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout

    def send(self, msg: Message) -> str:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            try:
                sock.sendto(msg.encode(), (self.host, self.port))
                sock.settimeout(self.timeout)
                return sock.recv(4096).decode()
            except socket.timeout:
                raise ClientError("Connection timed out.")

    def query(self, name: Optional[str]) -> str:
        if name is not None:
            return self.send(message.request(name))
        return self.send(message.random())


def main() -> None:
    parser = ArgumentParser(description="Fetch a random proof")
    parser.add_argument("name", nargs="?", default=None)
    parser.add_argument("--status-path", type=Path, default=consts.STATUS_PATH)
    parser.add_argument("-t", "--timeout", type=float, default=consts.CLIENT_TIMEOUT)
    parser.add_argument("-o", "--output", type=FileType("w"), default=sys.stdout)
    args = parser.parse_args()

    status = Status(args.status_path).read()
    if status is None:
        sys.exit("Daemon is not running.")

    client = ProofClient(status["host"], status["port"], args.timeout)
    try:
        print(client.query(args.name), file=args.output)
    except ClientError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
