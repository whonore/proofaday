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
from typing import Any, List, Optional, NoReturn, Tuple, Union

import requests
from bs4 import BeautifulSoup as BS  # type: ignore

from .syms import latex_to_text

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
NPREFETCH = 10
PROOF_END = re.compile(r"blacksquare")
HOST = "localhost"
PORT = 48484
SERVER_TRIES = 10
MAX_REQUESTS = 5
LOG_PATH = Path(__file__).parent / "proofaday.log"
MAX_LOG_BYTES = 1024 * 1024
TEST_PAGES = (
    "Union_of_Left-Total_Relations_is_Left-Total",
    "Frattini's_Argument",
    "Floor_of_Ceiling_is_Ceiling",
    "Existence_of_Unique_Subsemigroup_Generated_by_Subset",
    "Largest_Rectangle_with_Given_Perimeter_is_Square",
    "Event_Independence_is_Symmetric",
    "Inverse_of_Algebraic_Structure_Isomorphism_is_Isomorphism/General_Result",
    "If Every Element Pseudoprime is Prime then Way Below Relation is Multiplicative",
)


def node_to_text(node: Any) -> str:
    if node.name == "p":
        return node.get_text()  # type: ignore
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


def get_proof(name: Optional[str] = None) -> Optional[Tuple[str, str, str]]:
    if name is None:
        name = RANDOM
    url = URL + name

    html = BS(requests.get(url).text, "html.parser")
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

        return (
            title.get_text(),
            "".join(node_to_text(node) for node in theorem_body).strip(),
            "".join(node_to_text(node) for node in proof_body).strip(),
        )
    return None


def format_proof(title: str, theorem: str, proof: str) -> str:
    return "{}\n{}\n{}\n\nProof:\n{}".format(title, "=" * len(title), theorem, proof)


class MsgKind(IntEnum):
    CHECK = 1
    REQUEST = 2
    RANDOM = 3
    KILL = 4


class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self) -> None:
        msg, sock = self.request
        kind, msg = MsgKind(msg[0]), msg[1:]

        if kind is MsgKind.CHECK:
            msg = b""
        elif kind is MsgKind.REQUEST:
            proof = self.server.fetch_proof(str(msg, "utf8"))  # type: ignore
            msg = bytes(proof, "utf8") if proof is not None else b""
        elif kind is MsgKind.RANDOM:
            msg = bytes(self.server.queue.get(), "utf8")  # type: ignore
        elif kind is MsgKind.KILL:
            sock.sendto(b"", self.client_address)
            self.server.shutdown()
            return
        sock.sendto(msg, self.client_address)


class ProofServer(socketserver.ThreadingUDPServer):
    def __init__(
        self, port: int, limit: int, nprefetch: int, debug: bool, **kwargs: Any
    ) -> None:
        super().__init__((HOST, port), ProofHandler)
        level = logging.DEBUG if debug else logging.INFO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level)
        self.logger.addHandler(
            RotatingFileHandler(
                LOG_PATH, maxBytes=MAX_LOG_BYTES, backupCount=1, encoding="utf8"
            )
        )
        self.queue: Queue[str] = Queue(maxsize=nprefetch)
        self.limit = limit
        threading.Thread(target=self.fetch_proofs, daemon=True).start()

    def fetch_proof(self, name: Optional[str] = None) -> Optional[str]:
        try:
            res = get_proof(name)
            if res is not None:
                title, theorem, proof = res
                self.logger.debug(format_proof(title, theorem, proof))
                return format_proof(title, latex_to_text(theorem), latex_to_text(proof))
            return None
        except ConnectionResetError:
            return None
        except Exception:
            self.logger.exception("Exception while fetching a proof")
            return None

    def fetch_proofs(self) -> NoReturn:
        def enqueue_proof() -> None:
            proof = self.fetch_proof()
            if proof is not None and (
                self.limit is None or len(proof.split("\n")) <= self.limit
            ):
                self.queue.put(proof)

        while True:
            needed = max(min(self.queue.maxsize - self.queue.qsize(), MAX_REQUESTS), 1)
            workers = [threading.Thread(target=enqueue_proof) for _ in range(needed)]
            for worker in workers:
                worker.start()
            for worker in workers:
                worker.join()


def start_server(*args: Any, **kwargs: Any) -> None:
    with ProofServer(*args, **kwargs) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def msg_server(port: int, kind: MsgKind, data: str = "") -> Union[str, bool]:
    msg = bytes((kind,)) + bytes(data, "utf8")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(msg, (HOST, port))
        if kind in (MsgKind.CHECK, MsgKind.KILL):
            sock.settimeout(0.1)
            try:
                sock.recv(1)
                return True
            except socket.timeout:
                return False
        else:
            return str(sock.recv(4096), "utf8")


def check_server(port: int) -> bool:
    return msg_server(port, MsgKind.CHECK)  # type: ignore


def kill_server(port: int) -> bool:
    return msg_server(port, MsgKind.KILL)  # type: ignore


def query_server(port: int, name: Optional[str]) -> str:
    if name is not None:
        return msg_server(port, MsgKind.REQUEST, name)  # type: ignore
    else:
        return msg_server(port, MsgKind.RANDOM)  # type: ignore


def pos(arg: str) -> int:
    iarg = int(arg)
    if iarg <= 0:
        raise ValueError("not positive")
    return iarg


def main() -> None:
    parser = ArgumentParser(description="Fetch a random proof")
    parser.add_argument("name", nargs="?", default=None)
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("-l", "--limit", type=pos, default=None)
    parser.add_argument(
        "-n", "--num-prefetch-proofs", dest="nprefetch", type=pos, default=NPREFETCH
    )
    parser.add_argument("-p", "--port", type=int, default=PORT)
    parser.add_argument("-k", "--kill-server", dest="kill", action="store_true")
    args = parser.parse_args()

    if args.name is not None and args.name[0].isdigit():
        args.name = TEST_PAGES[int(args.name)]

    if args.kill:
        sys.exit(not kill_server(args.port))

    if not check_server(args.port):
        if os.fork() == 0:
            try:
                start_server(**vars(args))
                sys.exit()
            except OSError:
                sys.exit("Could not start server")
        else:
            for _ in range(SERVER_TRIES):
                if check_server(args.port):
                    break
            else:
                sys.exit("Could not connect to server")

    print(query_server(args.port, args.name))


if __name__ == "__main__":
    main()
