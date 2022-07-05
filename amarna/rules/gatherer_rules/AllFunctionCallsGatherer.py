from typing import List, Union
from dataclasses import dataclass

from lark import tree, Tree
from amarna.Result import PositionType, getPosition
from amarna.rules.GenericGatherer import GenericGatherer


@dataclass
class FunctionCallType:
    """Represents a function call."""

    file_name: str
    parent_function: str
    function_name: str
    tail_name: str
    position: PositionType
    arguments: Union[str, tree.Tree]


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

    def code_element_function(self, tree: Tree) -> None:
        parent_name: Optional[str] = None

        for child in tree.children:
            if child.data == "identifier_def":
                parent_name = str(child.children[0])
                break

        assert parent_name

        for func in tree.find_data("function_call"):
            func_id = func.children[0]
            # TODO (montyly): Mypy complains about .value not be present
            function_name: str = func_id.children[0].value  # type: ignore
            if len(func_id.children) > 1:
                tail_name: str = func_id.children[1].value  # type: ignore
            else:
                tail_name: str = None
            arguments = func.children[-1]

            function_call = FunctionCallType(
                self.fname, parent_name, function_name, tail_name, getPosition(func), arguments
            )
            self.function_calls.append(function_call)
