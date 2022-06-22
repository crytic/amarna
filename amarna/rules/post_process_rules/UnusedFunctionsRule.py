from typing import Dict, List
from amarna.Result import Result, create_result

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import (
    DeclaredFunctionsGatherer,
    FunctionType,
)
from amarna.rules.gatherer_rules.AllFunctionCallsGatherer import (
    AllFunctionCallsGatherer,
    FunctionCallType,
)
from amarna.rules.gatherer_rules.FunctionsUsedAsCallbacksGatherer import (
    CallbackFunctionType,
    FunctionsUsedAsCallbacksGatherer,
)
from amarna.rules.gatherer_rules.ImportGatherer import ImportGatherer, ImportType

# pylint: disable=too-few-public-methods
class UnusedFunctionsRule:
    """
    Match declared functions and called functions or callbacks to find unused functions.
    """

    RULE_TEXT = "This function is never called."
    RULE_NAME = "unused-function"

    # TODO: handle import shadowing other function names
    UNUSED_FP_DECORATORS = ["external", "view", "constructor", "l1_handler"]

    def run_rule(self, gathered_data: Dict) -> List[Result]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]
        function_calls: List[FunctionCallType] = gathered_data[
            AllFunctionCallsGatherer.GATHERER_NAME
        ]

        callbacks: List[CallbackFunctionType] = gathered_data[
            FunctionsUsedAsCallbacksGatherer.GATHERER_NAME
        ]

        import_stmts: List[ImportType] = gathered_data[ImportGatherer.GATHERER_NAME]

        results = []

        all_called = []
        for call in function_calls:
            all_called.append(call.function_name)

        for call in callbacks:
            all_called.append(call.function_name)

        # replace with actual function name if alias
        for imp in import_stmts:
            if not imp.alias_name:
                continue
            if imp.alias_name in all_called:
                all_called.remove(imp.alias_name)
                all_called.append(imp.import_name)

        for func in declared_functions:
            # ignore if it was called
            if func.name in all_called:
                continue

            # ignore cairo standard lib functions
            if "starkware/cairo/common/" in func.file_location:
                continue

            # ignore if it has a decorator that means it is not supposed to be called directly
            if any(decorator in self.UNUSED_FP_DECORATORS for decorator in func.decorators):
                continue

            result = create_result(
                func.file_location,
                self.RULE_NAME,
                self.RULE_TEXT,
                func.position,
            )
            results.append(result)

        return results
