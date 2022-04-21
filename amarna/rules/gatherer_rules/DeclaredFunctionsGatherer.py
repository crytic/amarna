from dataclasses import dataclass
from typing import Optional, List

from lark import Tree
from amarna.rules.GenericGatherer import GenericGatherer
from amarna.Result import getPosition, PositionType


@dataclass
class FunctionType:
    """Represents a function declaration."""

    name: str
    position: PositionType
    file_location: str
    decorators: List[str]


class DeclaredFunctionsGatherer(GenericGatherer):
    """
    Gather all declared functions.
    """

    GATHERER_NAME = "DeclaredFunctionsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.declared_functions: List[FunctionType] = []

    def get_gathered_data(self) -> List[FunctionType]:
        return self.declared_functions

    def code_element_function(self, tree: Tree) -> None:
        function_name: Optional[str] = None

        # find if the current tree is part of a @contract_interface
        # to ignore if unused in that case
        for struct in self.original_tree.find_data("code_element_struct"):
            for child in struct.find_data("decorator_list"):
                for decorator in child.find_data("identifier_def"):
                    if decorator.children[0] in ["contract_interface"]:
                        if tree in struct.iter_subtrees():
                            return

        # gather all decorators
        decorators = []
        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    decorators.append(str(decorator))

        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])
                break

        assert function_name

        func = FunctionType(function_name, getPosition(tree), self.fname, decorators)
        self.declared_functions.append(func)
