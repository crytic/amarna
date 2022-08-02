from lark import Tree, Token
from amarna.rules.GenericRule import GenericRule
from amarna.Result import (
    token_positions,
    result_multiple_positions,
)


class RevokedReferenceRule(GenericRule):
    """
    Check for usage of potentially revoked references.
    """

    RULE_TEXT = "Potentially revoked reference in use because of a function call inbetween reference [declaration](0) and [usage](1)."
    RULE_NAME = "revoked-reference"

    def code_block(self, tree: Tree) -> None:
        revokable_instr = ["code_element_func_call", "code_element_label"]
        for i, a in enumerate(tree.children):
            if a.children[0].data == "code_element_reference":
                tokens = list(a.scan_values(lambda v: isinstance(v, Token)))
                if all(str(tkn) != "ap" for tkn in tokens):
                    continue

                for j, b in enumerate(tree.children[i:]):
                    if b.children[0].data in revokable_instr:
                        for c in tree.children[(i + j + 1) :]:
                            usage = list(
                                c.scan_values(
                                    lambda v: isinstance(v, Token) and (str(v) == tokens[0])
                                )
                            )
                            for use in usage:
                                result = result_multiple_positions(
                                    [self.fname, self.fname],
                                    self.RULE_NAME,
                                    self.RULE_TEXT,
                                    [token_positions(tokens[0]), token_positions(use)],
                                )
                                if result.position_list not in (
                                    r.position_list for r in self.results
                                ):
                                    self.results.append(result)
