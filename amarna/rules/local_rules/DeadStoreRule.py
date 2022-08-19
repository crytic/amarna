from typing import Set

from lark import Tree, Token
from amarna.rules.GenericRule import GenericRule
from amarna.Result import create_result_token


class DeadStoreRule(GenericRule):
    """
    Check for dead dead_stores.
    """

    RULE_TEXT = "This variable is assigned or declared here but not used before a return statement."
    RULE_NAME = "dead-store"

    def code_element_function(self, tree: Tree) -> None:
        # pylint: disable=too-many-branches,too-many-nested-blocks,too-many-locals
        # gather implicit arguments
        implicits_and_arguments = []
        for impls in tree.find_data("implicit_arguments"):
            for args in impls.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        # gather argument names
        for allargs in tree.find_data("arguments"):
            for args in allargs.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        # gather call template names
        for allargs in tree.find_data("non_def_expr_assignment"):
            for args in allargs.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        # gather with_attr names
        for withattr in tree.find_data("code_element_with_attr"):
            for args in withattr.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        defines: Set[Token] = set()
        in_return = []
        for main_child in tree.children:
            if main_child.data != "code_block":
                continue

            for child in main_child.children:
                if child.children[0].data not in ["code_element_struct"]:
                    # add identifier definitions that aren't _, __fp__ or pc_val
                    for defn in child.find_data("identifier_def"):
                        if defn.children[0] not in ["_", "__fp__", "pc_val"]:
                            defines.add(defn.children[0])  # type: ignore

                    # remove identifier uses
                    for uses in child.find_data("identifier"):
                        tok = uses.children[0]
                        if tok in defines:
                            defines.remove(tok)  # type: ignore

                    # add lvalues. These can be false positives
                    # when a = b is an assert and not an assignment
                    for a in child.find_data("inst_assert_eq"):
                        for children_id in a.children[0].find_data("identifier"):
                            defines.add(children_id.children[0])  # type: ignore

                    # in a return statement, check which variables were not used
                    for subcode in child.children[0].find_data("code_element_return"):
                        for tok in subcode.scan_values(lambda v: isinstance(v, Token)):
                            in_return.append(str(tok))

        for dead_store in sorted(defines):
            if dead_store in in_return or dead_store in implicits_and_arguments:
                continue
            sarif = create_result_token(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                dead_store,
            )
            if sarif in self.results:
                continue
            self.results.append(sarif)
