from lark import tree, Visitor
from typing import Any, Dict

from output_sarif import *
from rules.GenericRule import GenericRule


def getPosition(tree: tree.Tree) -> tuple[int, int, int, int]:
    if hasattr(tree, "meta"):
        meta = tree.meta
        return (meta.line, meta.column, meta.end_line, meta.end_column)


class ArithmeticOperationsRule(GenericRule):
    """
    Check arithmetic operations:
        - reports ALL multiplications and divisions
        - reports ONLY addition and subtraction that do not involve a register like [ap - 1]
    """

    RULE_TEXT = "Cairo arithmetic is defined over a finite field and has potential for overflows."
    RULE_PREFIX = "arithmetic-"

    def expr_mul(self, tree):
        sarif = generic_sarif(
            self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree)
        )
        self.results.append(sarif)

    def expr_div(self, tree):
        sarif = generic_sarif(
            self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree)
        )
        self.results.append(sarif)

    def expr_add(self, tree: tree.Tree):
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        sarif = generic_sarif(
            self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree)
        )
        self.results.append(sarif)

    def expr_sub(self, tree: tree.Tree):
        # ignore subtracting to registers
        if tree.children[0].data == "atom_reg":
            return

        sarif = generic_sarif(
            self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree)
        )
        self.results.append(sarif)
