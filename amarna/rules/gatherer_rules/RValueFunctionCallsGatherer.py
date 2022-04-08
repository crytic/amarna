from typing import List, Tuple, Any

from lark import Tree


from amarna.rules.GenericGatherer import GenericGatherer


class RValueFunctionCallsGatherer(GenericGatherer):
    """
    Gather function calls that return to a variable, and their return values.
    """

    GATHERER_NAME = "RValueFunctionCallsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls: List[Tuple[str, str, Any]] = []

    def get_gathered_data(self) -> List[Tuple[str, str, Any]]:
        return self.function_calls

    def code_element_reference(self, tree: Tree) -> None:

        children = tree.children
        if len(children) != 2 or children[1].data != "rvalue_expr":
            return

        rvalues = children[1]
        returned_values = children[0]

        returned_list = list(returned_values.find_data("identifier_def"))

        for func in rvalues.find_data("function_call"):
            func_id = func.children[0]
            # TODO (montyly): mypy complain that the next element has no attribute value
            function_name = func_id.children[0].value  # type: ignore
            tup = (self.fname, function_name, returned_list)
            self.function_calls.append(tup)
