from lark import tree, Visitor, Token
from typing import Any, Dict, List, Set

from output_sarif import *


class UnusedArgumentRule(Visitor):
    """
    Check for unused arguments inside a function

    TODO: remove false positives from functions from a @contract_interface
    """

    def run_rule(self, fname: str, tree: tree.Tree):
        self.fname = fname
        self.results = []
        self.visit(tree)
        return self.results

    def get_results(self):
        return self.results

    # visit the code_element_function node of the AST
    def code_element_function(self, tree: tree.Tree):
        arguments = set()
        for child in tree.children:
            # get the function name
            if child.data == "identifier_def":
                function_name = child.children[0]

            # get the arguments names
            elif child.data == "arguments":
                for args in child.find_data("identifier_def"):
                    arguments.add(args.children[0])

            # get the function code ASTree
            elif child.data == "code_block":
                code_block = child

        used_ids: Set[Token] = set()
        for code_child in code_block.find_data("identifier"):
            used_ids.add(code_child.children[0])

        unused_arguments = arguments - used_ids
        for arg in unused_arguments:
            positions = (arg.line, arg.column, arg.end_line, arg.end_column)
            sarif = generic_sarif(
                self.fname,
                "unused_arguments",
                "Unused arguments might indicate a misspelled variable use or unnecessary argument.",
                positions,
            )
            self.results.append(sarif)
