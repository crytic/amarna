from typing import Dict, Any, List, Tuple
from amarna.output_sarif import generic_sarif, PositionType

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import DeclaredFunctionsGatherer
from amarna.rules.gatherer_rules.AllFunctionCallsGatherer import AllFunctionCallsGatherer
from amarna.rules.gatherer_rules.FunctionsUsedAsCallbacksGatherer import (
    FunctionsUsedAsCallbacksGatherer,
)

# pylint: disable=too-few-public-methods
class UnusedFunctionsRule:
    """
    Match declared functions and called functions or callbacks to find unused functions.
    """

    RULE_TEXT = "This function is never called."
    RULE_NAME = "unused-function"

    # TODO: handle interfaces and import shadowing other function names

    def run_rule(self, gathered_data: Dict) -> List[Dict[str, Any]]:
        declared_functions: Dict[str, Tuple[PositionType, str]] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]
        function_calls = gathered_data[AllFunctionCallsGatherer.GATHERER_NAME]

        callbacks = gathered_data[FunctionsUsedAsCallbacksGatherer.GATHERER_NAME]

        results = []
        for call in function_calls:
            _, function_name, _ = call

            if function_name in declared_functions:
                del declared_functions[function_name]

        for call in callbacks:
            _, function_name = call

            if function_name in declared_functions:
                del declared_functions[function_name]
        for unused in declared_functions:
            (position, file_name) = declared_functions[unused]

            # ignore cairo standard lib functions
            if "starkware/cairo/common/" in file_name:
                continue

            sarif = generic_sarif(
                file_name,
                self.RULE_NAME,
                self.RULE_TEXT,
                position,
            )
            results.append(sarif)

        return results
