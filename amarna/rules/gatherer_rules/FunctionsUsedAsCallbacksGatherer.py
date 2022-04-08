from typing import Tuple, List

from lark import Tree

from amarna.rules.GenericGatherer import GenericGatherer


class FunctionsUsedAsCallbacksGatherer(GenericGatherer):
    """
    Gather all function that are used as callbacks.
    """

    GATHERER_NAME = "FunctionsUsedAsCallbacks"

    def __init__(self) -> None:
        super().__init__()
        self.function_calls: List[Tuple[str, str]] = []

    def get_gathered_data(self) -> List[Tuple[str, str]]:
        return self.function_calls

    def function_call(self, tree: Tree) -> None:

        children_id = tree.children[0]
        # TODO (montyly): attribute access error
        function_name = children_id.children[0].value  # type: ignore
        if function_name == "serialize_array":
            arguments = tree.children[1]
            callback_arg = arguments.children[-1]
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

            tup = (self.fname, str(token))
            self.function_calls.append(tup)

        elif function_name == "get_label_location":
            for identifier in tree.find_data("atom_identifier"):
                token = identifier.children[0].children[0]
                tup = (self.fname, str(token))

                self.function_calls.append(tup)
