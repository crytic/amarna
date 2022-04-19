from typing import Tuple, Dict, Optional

from lark import Tree
from amarna.rules.GenericGatherer import GenericGatherer
from amarna.Result import getPosition, PositionType


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

        # TODO: add decorator list to function info, and filter these
        # on the unused function rule instead.

        # find if the current tree is part of a @contract_interface
        # to ignore if unused in that case
        for struct in self.original_tree.find_data("code_element_struct"):
            for child in struct.find_data("decorator_list"):
                for decorator in child.find_data("identifier_def"):
                    if decorator.children[0] in ["contract_interface"]:
                        if tree in struct.iter_subtrees():
                            return

        # find if the function has external or view decorator
        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    if decorator in ["external", "view"]:
                        return


        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])
                break

        assert function_name

        # TODO: handle function name shadowing.
        # if function_name in self.declared_functions:
        #     print(f"[!] two functions declared with the same name: {function_name}")

        self.declared_functions[function_name] = (getPosition(tree), self.fname)
