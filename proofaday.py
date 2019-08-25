import re

import requests
from bs4 import BeautifulSoup as BS
from pylatexenc.latex2text import (
    LatexNodes2Text,
    get_default_latex_context_db as l2t_ctx,
    MacroTextSpec,
)
from pylatexenc.latexwalker import (
    get_default_latex_context_db as lwalk_ctx,
    LatexWalker,
)
from pylatexenc.macrospec import std_macro

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
MAX_RETRY = 5
tmps = (
    None,
    "Union_of_Left-Total_Relations_is_Left-Total",  # missing
    "Frattini's_Argument",  # missing
    "Floor_of_Ceiling_is_Ceiling",  # missing some text
    "Existence_of_Unique_Subsemigroup_Generated_by_Subset",
    "Largest_Rectangle_with_Given_Perimeter_is_Square",
)
tmp = tmps[-1]

MACROS = [
    MacroTextSpec(name, simplify_repl=repl)
    for name, repl in (
        ("R", "\N{DOUBLE-STRUCK CAPITAL R}"),
        ("Z", "\N{DOUBLE-STRUCK CAPITAL Z}"),
        ("N", "\N{DOUBLE-STRUCK CAPITAL N}"),
        ("lfloor", "\N{LEFT FLOOR}"),
        ("rfloor", "\N{RIGHT FLOOR}"),
        ("lceil", "\N{LEFT CEILING}"),
        ("rceil", "\N{RIGHT CEILING}"),
        ("blacksquare", "\N{BLACK SQUARE}"),
        ("in", "\N{ELEMENT OF} "),
        ("dfrac", "%s/%s"),
    )
]
MACRO_ARGS = [std_macro("dfrac", False, 2)]

CTX = l2t_ctx()
CTX.add_context_category("mathjax", macros=MACROS, prepend=True)
ARGS = lwalk_ctx()
ARGS.add_context_category("mathjax", macros=MACRO_ARGS, prepend=True)

L2T = LatexNodes2Text(CTX, math_mode="text")


def to_text(tag):
    if tag.name == "p":
        return tag.get_text()
    elif tag.name == "dl":
        return "\\qquad{}\n".format(tag.get_text())
    elif tag.name == "table":
        txt = []
        for row in tag.find_all("tr"):
            row_txt = []
            for el in row.find_all("td"):
                el_txt = el.get_text().strip()
                if el_txt != "":
                    row_txt.append(el_txt)
            txt.append(r"\qquad" + r"\ ".join(row_txt))
        return r"\\".join(txt)


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
        # TODO: strip text after proof end
        if title is not None and theorem is not None and proof is not None:
            tags = ["p", "dl", "table"]
            theorem_body = theorem.parent.find_next_siblings(tags)
            proof_body = proof.parent.find_next_siblings(tags)
            theorem_body = theorem_body[: -len(proof_body)]

            return (
                title.get_text(),
                "".join(to_text(tag) for tag in theorem_body).strip(),
                "".join(to_text(tag) for tag in proof_body).strip(),
            )
        elif name != RANDOM:
            return None
    return None


if __name__ == "__main__":
    ret = get_proof(tmp)
    if ret is not None:
        title, theorem, proof = ret
        theorem, proof = (
            L2T.latex_to_text(theorem, latex_context=ARGS),
            L2T.latex_to_text(proof, latex_context=ARGS),
        )
        print(
            "{}\n{}\n{}\n\nProof:\n{}".format(title, "=" * len(title), theorem, proof)
        )
