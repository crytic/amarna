from lark import tree, Visitor
from typing import Any, Dict

from output_sarif import *


def getPosition(tree: tree.Tree) -> tuple[int, int, int, int]:
    if hasattr(tree, "meta"):
        meta = tree.meta
        return (meta.line, meta.column, meta.end_line, meta.end_column)


def sarif_out(filename: str, tree: tree.Tree) -> Dict[str, Any]:
    start_line, start_col, end_line, end_col = getPosition(tree)
    return {
        "ruleId": f"arithmetic-{tree.data}",
        "level": "warning",
        "message": {
            "text": "Cairo arithmetic is defined over a finite field and has potential for overflows."
        },
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": {
                        "startLine": start_line,
                        "startColumn": start_col,
                        "endLine": end_line,
                        "endColumn": end_col,
                    },
                }
            }
        ],
    }


class ArithmeticOperationsRule(Visitor):
    """
    Check arithmetic operations:
        - reports ALL multiplications and divisions
        - reports ONLY addition and subtraction that do not involve a register like [ap - 1]
    """

    def run_rule(self, fname: str, tree: tree.Tree):
        self.fname = fname
        self.results = []
        self.visit(tree)
        return self.results

    def get_results(self):
        return self.results

    def expr_mul(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    def expr_div(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    def expr_add(self, tree: tree.Tree):
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        self.results.append(sarif_out(self.fname, tree))

    def expr_sub(self, tree: tree.Tree):
        # ignore subtracting to registers
        if tree.children[0].data == "atom_reg":
            return

        self.results.append(sarif_out(self.fname, tree))
