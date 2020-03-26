import concurrent.futures as futures
import logging
import os
import re
import socket
import socketserver
import sys
import threading
from argparse import ArgumentParser
from enum import IntEnum
from logging.handlers import RotatingFileHandler
from pathlib import Path
from queue import Queue
from typing import Any, List, NoReturn, Optional, Set, Union, overload
from typing_extensions import Literal

import requests
from bs4 import BeautifulSoup as BS  # type: ignore[import]
from requests import exceptions as exs

from .syms import latex_to_text

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
NPREFETCH = 10
PROOF_END = re.compile("blacksquare")
HOST = "localhost"
PORT = 48484
SERVER_TIMEOUT = 1
CLIENT_TIMEOUT = 3
LOG_PATH = Path(__file__).parent / "proofaday.log"


class Proof:
    def __init__(self, title: str, theorem: str, proof: str) -> None:
        self.title = title
        self._theorem = theorem
        self._proof = proof
        self.theorem = latex_to_text(theorem)
        self.proof = latex_to_text(proof)

    def __repr__(self) -> str:
        return (
            f"Proof(title={self.title}, theorem={self._theorem}, proof={self._proof})"
        )

    def __str__(self) -> str:
        return (
            f"{self.title}\n{'=' * len(self.title)}\n"
            f"{self.theorem}\n\nProof:\n{self.proof}"
        )


class MsgKind(IntEnum):
    CHECK = 1
    REQUEST = 2
    RANDOM = 3
    KILL = 4


class ProofServerError(Exception):
    pass


def node_to_text(node: Any) -> str:
    if node.name == "p":
        return node.get_text()  # type: ignore[no-any-return]
    elif node.name == "dl":
        return "\\qquad{}\n".format(node.get_text())
    elif node.name == "table":
        txt = []
        for row in node.find_all("tr"):
            row_txt: List[str] = []
            for el in row.find_all("td"):
                row_txt += list(el.stripped_strings)
            txt.append(r"\qquad" + r"\ ".join(row_txt))
        return r"\\".join(txt) + "\n"
    raise ValueError(node.name)


def get_proof(name: Optional[str] = None) -> Optional[Proof]:
    if name is None:
        name = RANDOM
    url = URL + name

    html = BS(requests.get(url, timeout=SERVER_TIMEOUT).text, "html.parser")
    title = html.find("h1", id="firstHeading")
    body = html.find("div", id="bodyContent")
    theorem = body.find("span", id="Theorem")
    proof = body.find("span", id="Proof")

    if title is not None and theorem is not None and proof is not None:
        tags = ("p", "dl", "table")
        theorem_body = theorem.parent.find_next_siblings(tags)
        proof_body = proof.parent.find_next_siblings(tags)
        theorem_body = theorem_body[: -len(proof_body)]

        if theorem_body == [] or proof_body == []:
            return None

        # Strip text after proof end
        for idx, node in enumerate(proof_body):
            if node.find(string=PROOF_END) is not None:
                proof_body = proof_body[: idx + 1]
                break
        else:
            # No proof end found
            return None

        return Proof(
            title.get_text(),
            "".join(node_to_text(node) for node in theorem_body).strip(),
            "".join(node_to_text(node) for node in proof_body).strip(),
        )
    return None


class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        data, sock = self.request
        kind, msg = MsgKind(data[0]), data[1:].decode()
        server: ProofServer = self.server  # type: ignore[assignment]

        if kind is MsgKind.CHECK:
            reply = ""
        elif kind is MsgKind.REQUEST:
            proof = server.fetch_proof(msg)
            reply = proof if proof is not None else ""
        elif kind is MsgKind.RANDOM:
            reply = server.queue.get()
        elif kind is MsgKind.KILL:
            sock.sendto(b"", self.client_address)
            server.shutdown()
            return
        sock.sendto(reply.encode(), self.client_address)


class ProofServer(socketserver.ThreadingUDPServer):
    max_log_bytes = 1024 * 1024
    max_requests = 5

    def __init__(
        self, port: int, limit: int, nprefetch: int, debug: bool, **kwargs: Any
    ) -> None:
        super().__init__((HOST, port), ProofHandler)
        level = logging.DEBUG if debug else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.logger.addHandler(
            RotatingFileHandler(
                LOG_PATH,
                maxBytes=ProofServer.max_log_bytes,
                backupCount=1,
                encoding="utf8",
            )
        )
        self.queue: Queue[str] = Queue(maxsize=nprefetch)
        self.limit = limit
        threading.Thread(target=self.fetch_proofs, daemon=True).start()

    def fetch_proof(self, name: Optional[str] = None) -> Optional[str]:
        try:
            proof = get_proof(name)
            if proof is not None:
                self.logger.debug(repr(proof))
                return str(proof)
            return None
        except (ConnectionResetError, exs.Timeout):
            return None
        except Exception as e:
            self.logger.exception(
                "Unexpected exception while fetching a proof: %s", str(e)
            )
            return None

    def enqueue_proof(self) -> None:
        proof = self.fetch_proof()
        if proof is not None and (
            self.limit is None or len(proof.split("\n")) <= self.limit
        ):
            self.queue.put(proof)

    def fetch_proofs(self) -> NoReturn:
        with futures.ThreadPoolExecutor(ProofServer.max_requests) as pool:
            jobs: Set[futures.Future[None]] = set()
            while True:
                njobs = self.queue.maxsize - self.queue.qsize() - len(jobs)
                if len(jobs) == 0:
                    njobs = max(njobs, 1)
                jobs |= {pool.submit(self.enqueue_proof) for _ in range(njobs)}
                done, _ = futures.wait(jobs, return_when=futures.FIRST_COMPLETED)
                jobs -= done


def daemon(*args: Any, **kwargs: Any) -> None:
    try:
        with ProofServer(*args, **kwargs) as server:
            server.serve_forever()
    except KeyboardInterrupt:
        pass
    sys.exit()


class ProofClient:
    retries = 10

    def __init__(self, port: int, timeout: float) -> None:
        self.port = port
        self.timeout = timeout

    @overload
    def msg(self, kind: Literal[MsgKind.CHECK, MsgKind.KILL], data: str = ...) -> bool:
        ...

    @overload
    def msg(
        self, kind: Literal[MsgKind.REQUEST, MsgKind.RANDOM], data: str = ...
    ) -> str:
        ...

    def msg(self, kind: MsgKind, data: str = "") -> Union[str, bool]:
        msg = bytes((kind,)) + data.encode()
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(msg, (HOST, self.port))
            if kind in (MsgKind.CHECK, MsgKind.KILL):
                sock.settimeout(0.1)
                try:
                    sock.recv(1)
                    return True
                except socket.timeout:
                    return False
            else:
                sock.settimeout(self.timeout)
                try:
                    return sock.recv(4096).decode()
                except socket.timeout:
                    return "Server timed out."

    def spawn(self, *args: Any, **kwargs: Any) -> None:
        try:
            if os.fork() == 0:
                daemon(*args, **kwargs)
            else:
                for _ in range(ProofClient.retries):
                    if self.check():
                        break
                else:
                    raise ProofServerError("Failed to connect to server.")
        except OSError:
            raise ProofServerError("Failed to spawn server.")

    def check(self) -> bool:
        return self.msg(MsgKind.CHECK)

    def kill(self) -> bool:
        return self.msg(MsgKind.KILL)

    def query(self, name: Optional[str]) -> str:
        if name is not None:
            return self.msg(MsgKind.REQUEST, name)
        return self.msg(MsgKind.RANDOM)


def main() -> None:
    def pos(arg: str) -> int:
        if int(arg) <= 0:
            raise ValueError("not positive")
        return int(arg)

    parser = ArgumentParser(description="Fetch a random proof")
    parser.add_argument("name", nargs="?", default=None)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-l", "--limit", type=pos, default=None)
    parser.add_argument(
        "-n", "--num-prefetch-proofs", dest="nprefetch", type=pos, default=NPREFETCH
    )
    parser.add_argument("-p", "--port", type=int, default=PORT)
    parser.add_argument("-t", "--timeout", type=float, default=CLIENT_TIMEOUT)
    parser.add_argument("-k", "--kill-server", dest="kill", action="store_true")
    args = parser.parse_args()

    client = ProofClient(args.port, args.timeout)
    try:
        if args.kill:
            sys.exit(not client.kill())
        if not client.check():
            client.spawn(**vars(args))
        print(client.query(args.name))
    except ProofServerError as e:
        sys.exit(str(e))


if __name__ == "__main__":
    main()
