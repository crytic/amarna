from dataclasses import dataclass
from typing import List

from lark import Tree
from amarna.Result import PositionType, getPosition

from amarna.rules.GenericGatherer import GenericGatherer


@dataclass
class CallbackFunctionType:
    """Represents a function callback."""

    file_name: str
    function_name: str
    position: PositionType


class FunctionsUsedAsCallbacksGatherer(GenericGatherer):
    """
    Gather all functions that are used as callbacks.
    """

    GATHERER_NAME = "FunctionsUsedAsCallbacks"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls: List[CallbackFunctionType] = []

    def get_gathered_data(self) -> List[CallbackFunctionType]:
        return self.function_calls

    def function_call(self, tree: Tree) -> None:

        children_id = tree.children[0]
        # TODO (montyly): attribute access error
        function_name = children_id.children[0].value  # type: ignore
        if function_name == "serialize_array":
            arguments = tree.children[1].children[0]
            callback_arg = arguments.children[-3]
            ids = list(callback_arg.find_data("identifier"))
            # variable callback
            if len(ids) == 1:
                token = ids[0].children[0]

            # manually callback such as asset_config_hash_serialize + __pc__ - ret_pc_label
            # TODO: check ast for name + __pc__ - ret_pc_label
            elif len(ids) == 3:
                # also idx 0
                token = ids[0].children[0]

            else:
                raise Exception(
                    "Function call path not implemented in amarna, please open an issue"
                )

            # add to the gatherer data
            callback = CallbackFunctionType(self.fname, str(token), getPosition(tree))
            self.function_calls.append(callback)

        elif function_name == "get_label_location":
            for identifier in tree.find_data("atom_identifier"):
                token = identifier.children[0].children[0]

                # add to the gatherer data
                callback = CallbackFunctionType(self.fname, str(token), getPosition(tree))
                self.function_calls.append(callback)
