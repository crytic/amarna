from lark import Tree

from amarna.rules.GenericRule import GenericRule
from amarna.Result import create_result, getPosition


class ArithmeticOperationsRule(GenericRule):
    """
    Check arithmetic operations:
        - reports ALL multiplications and divisions
        - reports ONLY addition and subtraction that do not involve a register like [ap - 1]
    """

    RULE_TEXT = "Cairo arithmetic is defined over a finite field and has potential for overflows."
    RULE_PREFIX = "arithmetic-"

    def expr_mul(self, tree: Tree) -> None:
        result = create_result(self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)

    def expr_div(self, tree: Tree) -> None:
        result = create_result(self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)

    def expr_add(self, tree: Tree) -> None:
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        result = create_result(self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)

    def expr_sub(self, tree: Tree) -> None:
        # ignore subtracting to registers
        if tree.children[0].data == "atom_reg":
            return

        result = create_result(self.fname, self.RULE_PREFIX + tree.data, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)
