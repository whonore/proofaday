import re
import os
import socket
import socketserver
import sys
import threading
from argparse import ArgumentParser
from enum import IntEnum
from queue import Queue

import requests
from bs4 import BeautifulSoup as BS

from syms import latex_to_text

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
NPREFETCH = 10
PROOF_END = re.compile(r"blacksquare")
PORT = 48484
HOST = "localhost"
SERVER_TRIES = 10
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


def node_to_text(node):
    if node.name == "p":
        return node.get_text()
    elif node.name == "dl":
        return "\\qquad{}\n".format(node.get_text())
    elif node.name == "table":
        txt = []
        for row in node.find_all("tr"):
            row_txt = []
            for el in row.find_all("td"):
                row_txt += list(el.stripped_strings)
            txt.append(r"\qquad" + r"\ ".join(row_txt))
        return r"\\".join(txt) + "\n"


def get_proof(name=None):
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

        return (
            title.get_text(),
            "".join(node_to_text(node) for node in theorem_body).strip(),
            "".join(node_to_text(node) for node in proof_body).strip(),
        )
    return None


def format_proof(title, theorem, proof):
    return "{}\n{}\n{}\n\nProof:\n{}".format(title, "=" * len(title), theorem, proof)


class MsgKind(IntEnum):
    CHECK = 1
    REQUEST = 2
    RANDOM = 3
    KILL = 4


class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self):
        msg, sock = self.request
        kind, msg = MsgKind(msg[0]), msg[1:]

        if kind is MsgKind.CHECK:
            msg = b""
        elif kind is MsgKind.REQUEST:
            proof = self.server.fetch_proof(str(msg, "utf8"))
            msg = bytes(proof, "utf8") if proof is not None else b""
        elif kind is MsgKind.RANDOM:
            msg = bytes(self.server.queue.get(), "utf8")
        elif kind is MsgKind.KILL:
            sock.sendto(b"", self.client_address)
            self.server.shutdown()
            return
        sock.sendto(msg, self.client_address)


class ProofServer(socketserver.ThreadingUDPServer):
    def __init__(self, port, limit, nprefetch, **kwargs):
        super().__init__((HOST, port), ProofHandler)
        self.queue = Queue(maxsize=nprefetch)
        self.limit = limit
        self.fetcher = threading.Thread(target=self.fetch_proofs)
        self.fetcher.daemon = True
        self.fetcher.start()

    def fetch_proof(self, name=None):
        try:
            title, theorem, proof = get_proof(name)
        except TypeError:
            return None
        except ConnectionResetError:
            return None

        # if debug:
        #     print("===DEBUG===")
        #     print(format_proof(title, theorem, proof))
        #     print("===DEBUG===\n")

        return format_proof(title, latex_to_text(theorem), latex_to_text(proof))

    def fetch_proofs(self):
        while True:
            proof = self.fetch_proof()
            if proof is not None and (
                self.limit is None or len(proof.split("\n")) <= self.limit
            ):
                self.queue.put(proof)


def start_server(*args, **kwargs):
    with ProofServer(*args, **kwargs) as server:
        server.serve_forever()


def msg_server(port, kind, data=""):
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


def check_server(port):
    return msg_server(port, MsgKind.CHECK)


def kill_server(port):
    return msg_server(port, MsgKind.KILL)


def query_server(port, name):
    if name is not None:
        return msg_server(port, MsgKind.REQUEST, bytes(name, "utf8"))
    else:
        return msg_server(port, MsgKind.RANDOM)


def pos(arg):
    arg = int(arg)
    if arg <= 0:
        raise ValueError("not positive")
    return arg


if __name__ == "__main__":
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
