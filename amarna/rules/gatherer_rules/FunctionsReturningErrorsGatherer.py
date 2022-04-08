from typing import Dict, Optional

from lark import Tree

from amarna.rules.GenericGatherer import GenericGatherer

FunctionReturningType = Dict[str, int]


class FunctionsReturningErrorsGatherer(GenericGatherer):
    GATHERER_NAME = "FunctionsReturningErrorsGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.functions_returning_errors: FunctionReturningType = {}

    def get_gathered_data(self) -> FunctionReturningType:
        return self.functions_returning_errors

    def code_element_function(self, tree: Tree) -> None:
        return_code_pos = -1
        function_name: Optional[str] = None
        for child in tree.children:
            if child.data == "identifier_def":
                function_name = str(child.children[0])

            elif child.data == "identifier_list":
                for idx, args in enumerate(child.find_data("identifier_def")):
                    return_name = args.children[0]

                    if "return_code" in return_name or "success" in return_name:
                        return_code_pos = idx

        if return_code_pos == -1:
            return

        assert function_name

        self.functions_returning_errors[function_name] = return_code_pos
