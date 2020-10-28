import socket
import sys
from pathlib import Path
from typing import IO, Optional

import click

import proofaday.constants as consts
import proofaday.message as message
from proofaday.cli_util import ClickPath
from proofaday.message import Message
from proofaday.status import Status


class ClientError(Exception):
    pass


class ProofClient:
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

    def query(self, proof: Optional[str]) -> str:
        if proof is not None:
            return self.send(message.request(proof))
        return self.send(message.random())


@click.command(help="Fetch a random proof.")
@click.argument("proof", required=False, default=None)
@click.option(
    "--status-path",
    help="Directory to place the status file.",
    type=ClickPath(exists=False, file_okay=False),
    default=consts.DATA_PATH,
)
@click.option(
    "-t",
    "--timeout",
    help="Time to wait for a proof (in seconds).",
    type=float,
    default=consts.CLIENT_TIMEOUT,
    show_default=True,
)
@click.option(
    "-o",
    "--output",
    help="The file to print output to.",
    type=click.File("w"),
    default=sys.stdout,
)
def main(
    proof: Optional[str],
    status_path: Path,
    timeout: float,
    output: IO[str],
) -> None:
    status = Status(status_path).read()
    if status is None:
        sys.exit("Daemon is not running.")

    client = ProofClient(status["host"], status["port"], timeout)
    try:
        click.echo(client.query(proof), file=output)
    except ClientError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
