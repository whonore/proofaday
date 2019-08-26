import re
import socket
import socketserver
import sys
import threading
from queue import Queue

import requests
from bs4 import BeautifulSoup as BS

from syms import latex_to_text

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
MAX_RETRY = 5
MAX_PROOFS = 10
PROOF_END = re.compile(r"blacksquare")
PORT = 48484
HOST = 'localhost'
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

    for _ in range(MAX_RETRY):
        html = BS(requests.get(url).text, "html.parser")
        title = html.find("h1", id="firstHeading")
        body = html.find("div", id="bodyContent")
        theorem = body.find("span", id="Theorem")
        proof = body.find("span", id="Proof")

        if title is not None and theorem is not None and proof is not None:
            tags = ["p", "dl", "table"]
            theorem_body = theorem.parent.find_next_siblings(tags)
            proof_body = proof.parent.find_next_siblings(tags)
            theorem_body = theorem_body[: -len(proof_body)]

            if theorem_body == [] or proof_body == []:
                if name != RANDOM:
                    break
                else:
                    continue

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
        elif name != RANDOM:
            break
    return None


def format_proof(title, theorem, proof):
    return "{}\n{}\n{}\n\nProof:\n{}".format(title, "=" * len(title), theorem, proof)

class ProofHandler(socketserver.BaseRequestHandler):
    def handle(self):
        msg, sock = self.request
        if msg != b'':
            proof = self.server.fetch_proof(str(msg, 'utf8'))
        else:
            proof = self.server.queue.get()
        sock.sendto(bytes(proof, 'utf8') if proof is not None else b'', self.client_address)

class ProofServer(socketserver.UDPServer):
    def __init__(self, port):
        super().__init__((HOST, port), ProofHandler)
        self.queue = Queue(maxsize=MAX_PROOFS)
        self.fetcher = threading.Thread(target=self.fetch_proofs)
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
            if proof is not None:
                self.queue.put(proof)

def start_server():
    with ProofServer(PORT) as server:
        server.serve_forever()

def query_server(name):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.sendto(bytes(name, 'utf8') if name is not None else b'', (HOST, PORT))
        return str(sock.recv(4096), 'utf8')

if __name__ == "__main__":
    try:
        idx = sys.argv.index("-d")
        sys.argv.pop(idx)
        debug = True
    except ValueError:
        debug = False
    try:
        name = sys.argv[1]
        if name[0].isdigit():
            name = TEST_PAGES[int(name)]
    except IndexError:
        name = None

    try:
        start_server()
    except OSError:
        print(query_server(name))
