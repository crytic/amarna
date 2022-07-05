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

    results = []

    declared_functions = []
    function_calls = []

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        self.declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]
        self.function_calls: List[FunctionCallType] = gathered_data[
            AllFunctionCallsGatherer.GATHERER_NAME
        ]

        for func in self.function_calls:
            if func.tail_name == "write" or func.function_name == "storage_write":
                self.check_parents(func, func)
        return self.results

    def check_parents(self, call: FunctionCallType, original_call: FunctionCallType):
        for func in self.declared_functions:
            if func.name == call.parent_function:
                if any((decorator == "view") for decorator in func.decorators):
                    result = result_multiple_positions(
                        original_call.file_name,
                        func.file_location,
                        self.RULE_NAME,
                        self.RULE_TEXT,
                        [original_call.position, func.position],
                    )
                    if result.position_list not in (r.position_list for r in self.results):
                        self.results.append(result)
            # also recursively check if parents are called from view context
            for x in self.function_calls:
                if x.function_name == call.parent_function:
                    self.check_parents(x, original_call)
        return
