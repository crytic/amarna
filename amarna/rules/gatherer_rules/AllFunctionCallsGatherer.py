from lark import tree
from typing import Set


from amarna.output_sarif import *
from amarna.rules.GenericGatherer import GenericGatherer


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

    def function_call(self, func: tree.Tree):

        id = func.children[0]
        function_name = id.children[0].value
        arguments = func.children[-1]

        tup = (self.fname, function_name, arguments)

        self.function_calls.append(tup)
