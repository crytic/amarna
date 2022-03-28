from typing import Tuple, Any, List

from lark import tree
from amarna.rules.GenericGatherer import GenericGatherer

FunctionCallType = Tuple[str, str, Any]


class AllFunctionCallsGatherer(GenericGatherer[list]):
    """
    Gather all function calls independently of being an rvalue or a tail-call.
    """

    GATHERER_NAME = "AllFunctionCallsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls: List[FunctionCallType] = []

    def get_gathered_data(self) -> List[FunctionCallType]:
        return self.function_calls

    def function_call(self, func: tree.Tree) -> None:
        func_id = func.children[0]
        # TODO (montyly): Mypy complains about .value not be present
        function_name: str = func_id.children[0].value  # type: ignore
        arguments = func.children[-1]

        tup: Tuple[str, str, Any] = (self.fname, function_name, arguments)

        self.function_calls.append(tup)
