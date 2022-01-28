from lark import tree, Token

from amarna.output_sarif import *
from amarna.rules.GenericRule import GenericRule


class DeadStoreRule(GenericRule):
    """
    Check for dead dead_stores.
    """

    RULE_TEXT = "This variable is assigned or declared here but not used before a return statement."
    RULE_NAME = "dead-store"

    def code_element_function(self, tree: tree.Tree):
        # gather implicit arguments
        implicits_and_arguments = []
        for impls in tree.find_data("implicit_arguments"):
            for args in impls.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        # gather argument names
        for allargs in tree.find_data("arguments"):
            for args in allargs.find_data("identifier_def"):
                implicits_and_arguments.append(str(args.children[0]))

        defines = set()
        for main_child in tree.children:
            if main_child.data != "code_block":
                continue

            for child in main_child.children:
                if child.children[0].data not in ["code_element_struct"]:
                    # add identifier definitions that aren't _, __fp__ or pc_val
                    for defn in child.find_data("identifier_def"):
                        if defn.children[0] not in ["_", "__fp__", "pc_val"]:
                            defines.add(defn.children[0])

                    # remove identifier uses
                    for uses in child.find_data("identifier"):
                        tok = uses.children[0]
                        if tok in defines:
                            defines.remove(tok)

                    # add lvalues. These can be false positives when a = b is an assert and not an assignment
                    for a in child.find_data("inst_assert_eq"):
                        for id in a.children[0].find_data("identifier"):
                            defines.add(id.children[0])

                    # in a return statement, check which variables were not used
                    for subcode in child.children[0].find_data("code_element_return"):
                        tokens = [
                            str(tok)
                            for tok in subcode.scan_values(
                                lambda v: isinstance(v, Token)
                            )
                        ]
                        for dead_store in defines:
                            if (
                                dead_store in tokens
                                or dead_store in implicits_and_arguments
                            ):
                                continue
                            sarif = generic_sarif_token(
                                self.fname,
                                self.RULE_NAME,
                                self.RULE_TEXT,
                                dead_store,
                            )
                            if sarif in self.results:
                                continue
                            self.results.append(sarif)
