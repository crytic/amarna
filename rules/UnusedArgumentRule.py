from lark import tree, Token
from typing import Set

from output_sarif import *
from rules.GenericRule import GenericRule


class UnusedArgumentRule(GenericRule):
    """
    Check for unused arguments inside a function

    TODO: remove false positives from functions within a @contract_interface
    """

    RULE_TEXT = "Unused arguments might indicate a misspelled variable use or unnecessary argument."
    RULE_NAME = "unused-arguments"

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
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
