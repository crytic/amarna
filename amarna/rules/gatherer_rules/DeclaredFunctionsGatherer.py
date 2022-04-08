from typing import Tuple, Dict, Optional

from lark import Tree
from amarna.rules.GenericGatherer import GenericGatherer
from amarna.output_sarif import getPosition, PositionType


class DeclaredFunctionsGatherer(GenericGatherer):
    """
    Gather all declared functions.
    """

    GATHERER_NAME = "DeclaredFunctionsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.declared_functions: Dict[str, Tuple[PositionType, str]] = {}

    def get_gathered_data(self) -> Dict[str, Tuple[PositionType, str]]:
        return self.declared_functions

    def code_element_function(self, tree: Tree) -> None:
        function_name: Optional[str] = None
        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])
                break

        assert function_name

        # TODO: handle function name shadowing.
        # if function_name in self.declared_functions:
        #     print(f"[!] two functions declared with the same name: {function_name}")

        self.declared_functions[function_name] = (getPosition(tree), self.fname)
