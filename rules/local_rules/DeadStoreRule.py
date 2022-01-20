from lark import tree, Token
from typing import Set

from output_sarif import *
from rules.GenericRule import GenericRule


def subtree_data(tree: tree.Tree):
    return [str(t.data) for t in tree.iter_subtrees_topdown()]


def get_identifier_of(data, tree: tree.Tree):
    res = []
    for arg in tree.find_data(data):
        for ids in arg.find_data("identifier_def"):
            res.append(ids.children[0])
    return res[0]


class DeadStoreRule(GenericRule):
    """
    Check for dead dead_stores.
    """

    RULE_TEXT = (
        "This variable is assigned here but never used again before the function ends."
    )
    RULE_NAME = "dead-store"

    def code_element_function(self, tree: tree.Tree):
        # remaining assignment on this node:
        # inst_assert_eq

        dead_stores = set()
        for main_child in tree.children:
            if main_child.data != "code_block":
                continue

            for child in main_child.children:
                sub_data = subtree_data(child)
                if "code_element_temp_var" in sub_data:
                    id = get_identifier_of("code_element_temp_var", child)
                    dead_stores.add(id)

                elif "code_element_local_var" in sub_data:
                    id = get_identifier_of("code_element_local_var", child)
                    dead_stores.add(id)

                elif "inst_assert_eq" in sub_data:
                    for a in child.find_data("inst_assert_eq"):
                        for id in a.children[0].find_data("identifier"):
                            dead_stores.add(id.children[0])


                elif "code_element_return" in sub_data:
                    for arg in dead_stores:
                        positions = (arg.line, arg.column, arg.end_line, arg.end_column)
                        sarif = generic_sarif(
                            self.fname,
                            self.RULE_NAME,
                            self.RULE_TEXT,
                            positions,
                        )
                        self.results.append(sarif)
                    dead_stores = set()
                    break
                else:
                    for args in child.find_data("identifier"):
                        el = args.children[0]
                        if el in dead_stores:
                            dead_stores.remove(el)



