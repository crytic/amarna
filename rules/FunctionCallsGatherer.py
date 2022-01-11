from lark import tree
from typing import Set


from output_sarif import *
from rules.GenericGatherer import GenericGatherer


class FunctionCallsGatherer(GenericGatherer):
    """
    Gather function calls and their return values.
    """

    GATHERER_NAME = "FunctionCallsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls = []

    def get_gathered_data(self):
        return self.function_calls

    def code_element_reference(self, tree: tree.Tree):

        children = tree.children
        if len(children) != 2 or children[1].data != "rvalue_expr":
            return

        rvalues = children[1]
        returned_values = children[0]

        for func in rvalues.find_data("function_call"):
            id = func.children[0]
            function_name = id.children[0].value
            returned_list = [
                returned for returned in returned_values.find_data("identifier_def")
            ]
            tup = (self.fname, function_name, returned_list)
            self.function_calls.append(tup)
