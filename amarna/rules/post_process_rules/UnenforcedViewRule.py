from typing import Dict, List
from amarna.Result import ResultMultiplePositions, result_multiple_positions
from amarna.rules.GenericRule import GenericRule

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import (
    DeclaredFunctionsGatherer,
    FunctionType,
)
from amarna.rules.gatherer_rules.AllFunctionCallsGatherer import (
    AllFunctionCallsGatherer,
    FunctionCallType,
)


class UnenforcedViewRule(GenericRule):
    """
    Find state modifications in functions with @view decorator.
    """

    RULE_TEXT = (
        "[This](0) function call modifies state but is called within [this](1) @view context."
    )
    RULE_NAME = "unenforced-view"

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]
        function_calls: List[FunctionCallType] = gathered_data[
            AllFunctionCallsGatherer.GATHERER_NAME
        ]

        results = []

        def check_parents(call: FunctionCallType, original_call: FunctionCallType):
            for func in declared_functions:
                if func.name == call.parent_function:
                    if any((decorator == "view") for decorator in func.decorators):
                        result = result_multiple_positions(
                            original_call.file_name,
                            func.file_location,
                            self.RULE_NAME,
                            self.RULE_TEXT,
                            [original_call.position, func.position],
                        )
                        if result.position_list not in (r.position_list for r in results):
                            results.append(result)
                # also recursively check if parents are called from view context
                for x in function_calls:
                    if x.function_name == call.parent_function:
                        check_parents(x, original_call)

        for f in function_calls:
            if f.tail_name == "write" or f.function_name == "storage_write":
                check_parents(f, f)
        return results
