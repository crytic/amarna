from lark import tree
from typing import Set

from amarna.output_sarif import *
from amarna.rules.GenericRule import GenericRule


class UnknownDecoratorRule(GenericRule):
    """
    Check for misspelled function decorators.
    """

    RULE_TEXT = "Unknown of misspelled function decorator."
    RULE_NAME = "unknown-decorator"

    known_decorators = [
        "storage_var",
        "external",
        "view",
        "constructor",
        "l1_handler",
        "known_ap_change",
    ]

    def code_element_function(self, tree: tree.Tree):
        unknown_decorators = []
        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    if decorator not in self.known_decorators:
                        unknown_decorators.append(decorator)

        for arg in unknown_decorators:
            positions = (arg.line, arg.column, arg.end_line, arg.end_column)
            sarif = generic_sarif(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
