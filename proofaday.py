import re
import sys

import requests
from bs4 import BeautifulSoup as BS

from syms import latex_to_text

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
MAX_RETRY = 5
PROOF_END = re.compile(r"blacksquare")
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
        title, theorem, proof = get_proof(name)
    except TypeError:
        sys.exit(1)
    except ConnectionResetError:
        sys.exit(1)

    if debug:
        print("===DEBUG===")
        print(format_proof(title, theorem, proof))
        print("===DEBUG===\n")

    print(format_proof(title, latex_to_text(theorem), latex_to_text(proof)))
