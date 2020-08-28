import re
from typing import Any, List, Tuple

from typing_extensions import Final

from proofaday.syms import latex_to_text


class InvalidProofException(Exception):
    pass


class Proof:
    proof_end: Final = re.compile("blacksquare")
    tags: Final = ("p", "dl", "table")

    def __init__(self, html: Any) -> None:
        self.title, self._theorem, self._proof = self.parse(html)
        self.theorem = latex_to_text(self._theorem)
        self.proof = latex_to_text(self._proof)

    def parse(self, html: Any) -> Tuple[str, str, str]:
        title = html.find("h1", id="firstHeading")
        body = html.find("div", id="bodyContent")
        theorem = body.find("span", id="Theorem")
        proof = body.find("span", id="Proof")

        if any(x is None for x in (title, theorem, proof)):
            missing = [
                x
                for x, y in zip(("title", "theorem", "proof"), (title, theorem, proof))
                if y is None
            ]
            raise InvalidProofException(f"Missing {', '.join(missing)}.")

        theorem_body = theorem.parent.find_next_siblings(Proof.tags)
        proof_body = proof.parent.find_next_siblings(Proof.tags)
        theorem_body = theorem_body[: -len(proof_body)]

        if any(x == [] for x in (theorem_body, proof_body)):
            missing = [
                x + "body"
                for x, y in zip(("theorem", "proof"), (theorem_body, proof_body))
                if y == []
            ]
            raise InvalidProofException(f"Missing {', '.join(missing)}.")

        # Strip text after proof end
        for idx, node in enumerate(proof_body):
            if node.find(string=Proof.proof_end) is not None:
                proof_body = proof_body[: idx + 1]
                break
        else:
            # No proof end found
            raise InvalidProofException(f"Missing proof end ({Proof.proof_end})")

        return (
            title.get_text(),
            "".join(self.node_to_text(node) for node in theorem_body).strip(),
            "".join(self.node_to_text(node) for node in proof_body).strip(),
        )

    def node_to_text(self, node: Any) -> str:
        if node.name == "p":
            return node.get_text()  # type: ignore[no-any-return]
        elif node.name == "dl":
            return f"\\qquad{node.get_text()}\n"
        elif node.name == "table":
            txt = []
            for row in node.find_all("tr"):
                row_txt: List[str] = []
                for el in row.find_all("td"):
                    row_txt += list(el.stripped_strings)
                txt.append(r"\qquad" + r"\ ".join(row_txt))
            return r"\\".join(txt) + "\n"
        raise InvalidProofException(f"Invalid node {node.name}")

    def __repr__(self) -> str:
        return (
            f"Proof(title={self.title}, theorem={self._theorem}, proof={self._proof})"
        )

    def __str__(self) -> str:
        return (
            f"{self.title}\n{'=' * len(self.title)}\n"
            f"{self.theorem}\n\nProof:\n{self.proof}"
        )
