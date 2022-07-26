from functools import reduce
from typing import Callable, Tuple, Union, List
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


PRIME = 2**251 + 17 * 2**192 + 1


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        return None
    else:
        return x % m


def div(x, y):
    if x == None or y == None:
        return None
    return x * modinv(y, PRIME) % PRIME


def recursion_gather_operands(tree: Tree, numbers: List[int]):
    original_operation = tree.data

    for child in tree.children:
        data = child.data
        if data == "atom_number":
            num = child.children[0]
            numbers.append(int(str(num)))
        elif data == "notes":
            continue
        elif data == original_operation:
            recursion_gather_operands(child, numbers)
        else:
            # print("found node: ", data)
            return None

    return numbers


def is_potential_overflow(
    tree: Tree, op: Callable[[int, int], int]
) -> Tuple[Union[int, None], bool]:
    rec = recursion_gather_operands(tree, [])
    if not rec:
        return None, True

    result = reduce(op, rec)
    if not result:
        return None, True

    if result < 0 or result >= PRIME:
        return result, True

    return result, False


class MulArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "mul"

    def expr_mul(self, tree: Tree) -> None:
        res, overflow = is_potential_overflow(tree, lambda x, y: x * y)
        if not overflow:
            return

        text = self.RULE_TEXT
        if res:
            text += f" This multiplication will overflow and return {res % PRIME}."

        result = create_result(self.fname, self.RULE_NAME, text, getPosition(tree))
        self.results.append(result)


class DivArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "div"

    def expr_div(self, tree: Tree) -> None:
        res, _ = is_potential_overflow(tree, div)
        text = self.RULE_TEXT
        if res:
            text += f" This division will return {res}."

        result = create_result(self.fname, self.RULE_NAME, text, getPosition(tree))
        self.results.append(result)


class AddArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "add"

    def expr_add(self, tree: Tree) -> None:
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        res, overflow = is_potential_overflow(tree, lambda x, y: x + y)
        if not overflow:
            return

        text = self.RULE_TEXT
        if res:
            text += f" This addition will overflow and return {res % PRIME}."

        result = create_result(self.fname, self.RULE_NAME, text, getPosition(tree))
        self.results.append(result)


class SubArithmeticOperationsRule(ArithmeticOperationsRule):
    RULE_NAME = ArithmeticOperationsRule.RULE_PREFIX + "sub"

    def expr_sub(self, tree: Tree) -> None:
        # ignore subtracting to registers
        if tree.children[0].data == "atom_reg":
            return

        res, overflow = is_potential_overflow(tree, lambda x, y: x - y)
        if not overflow:
            return

        text = self.RULE_TEXT
        if res:
            text += f" This subtraction will overflow and return {res % PRIME}."

        result = create_result(self.fname, self.RULE_NAME, text, getPosition(tree))
        self.results.append(result)
