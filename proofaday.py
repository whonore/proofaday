import re

import requests
from bs4 import BeautifulSoup as BS
from pylatexenc.latex2text import (
    LatexNodes2Text as L2T,
    get_default_latex_context_db,
    MacroTextSpec
)
# from pylatexenc.macrospec import

URL = "https://proofwiki.org/wiki/"
RANDOM = "Special:Random"
MAX_RETRY = 5
tmps = (
    None,
    "Union_of_Left-Total_Relations_is_Left-Total", # missing
    "Frattini's_Argument", # missing
    "Floor_of_Ceiling_is_Ceiling", # missing some text
    "Existence_of_Unique_Subsemigroup_Generated_by_Subset",
    "Largest_Rectangle_with_Given_Perimeter_is_Square"
)
tmp = tmps[-1]

def get_proof(name=None):
    if name is None:
        name = RANDOM
    url = URL + name
    for _ in range(MAX_RETRY):
        html = BS(requests.get(url).text, 'html.parser')
        title = html.find('h1', id='firstHeading')
        body = html.find('div', id='bodyContent')
        theorem = body.find('span', id='Theorem')
        proof = body.find('span', id='Proof')
        # TODO: strip text after proof end
        if title is not None and theorem is not None and proof is not None:
            theorem_body = theorem.parent.find_next_siblings('p')
            proof_body = proof.parent.find_next_siblings('p')
            theorem_body = theorem_body[:-len(proof_body)]
            return (title.get_text(),
                    ''.join([x.get_text() for x in theorem_body]).strip(),
                    ''.join([x.get_text() for x in proof_body]).strip())
        elif name != RANDOM:
            return None
    return None

MACROS = [
    MacroTextSpec(*macro) for macro in [
        ('R', 'ℝ'), ('Z', 'ℤ'), ('N', 'ℕ'),
        ('lfloor', '⌊'), ('rfloor', '⌋'), ('lceil', '⌈'), ('rceil', '⌉'),
        ('blacksquare', '⬛'),
        ('in', '∈ ')
    ]
]

CTX = get_default_latex_context_db()
CTX.add_context_category('mathjax', macros=MACROS, prepend=True)

def asciify(math):
    return L2T(CTX, math_mode='text').latex_to_text(math)

if __name__ == '__main__':
    ret = get_proof(tmp)
    if ret is not None:
        title, theorem, proof = ret
        theorem, proof = asciify(theorem), asciify(proof)
        print(f"Theorem {title}\n{'=' * len('Theorem ' + title)}\n{theorem}\n\nProof:\n{proof}")
