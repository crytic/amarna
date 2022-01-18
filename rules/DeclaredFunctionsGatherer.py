from lark import tree
from typing import Set


from output_sarif import *
from rules.GenericGatherer import GenericGatherer
from output_sarif import getPosition


class DeclaredFunctionsGatherer(GenericGatherer):
    """
    Gather all declared functions.
    """

    GATHERER_NAME = "DeclaredFunctionsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.declared_functions = {}

    def get_gathered_data(self):
        return self.declared_functions

    def code_element_function(self, tree: tree.Tree):
        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])
                break

        # TODO: handle function name shadowing.
        if function_name in self.declared_functions:
            print(f"[!] two functions declared with the same name: {function_name}")

        self.declared_functions[function_name] = (getPosition(tree), self.fname)
