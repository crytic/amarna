from lark import tree
from typing import Set


from output_sarif import *
from rules.GenericGatherer import GenericGatherer


class AllFunctionCallsGatherer(GenericGatherer):
    """
    Gather all function calls independently of being an rvalue or a tail-call.
    """

    GATHERER_NAME = "AllFunctionCallsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls = []

    def get_gathered_data(self):
        return self.function_calls

    def code_block(self, tree: tree.Tree):

        for func in tree.find_data("function_call"):
            id = func.children[0]
            function_name = id.children[0].value

            tup = (self.fname, function_name)

            self.function_calls.append(tup)
