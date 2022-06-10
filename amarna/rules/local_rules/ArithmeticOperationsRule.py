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


class MulArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "mul"

    def expr_mul(self, tree: Tree) -> None:
        result = create_result(self.fname, self.RULE_NAME, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)


class DivArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "div"

    def expr_div(self, tree: Tree) -> None:
        result = create_result(self.fname, self.RULE_NAME, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)


class AddArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "add"

    def expr_add(self, tree: Tree) -> None:
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        result = create_result(self.fname, self.RULE_NAME, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)


class SubArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "sub"

    def expr_sub(self, tree: Tree) -> None:
        # ignore subtracting to registers
        if tree.children[0].data == "atom_reg":
            return

        result = create_result(self.fname, self.RULE_NAME, self.RULE_TEXT, getPosition(tree))
        self.results.append(result)
