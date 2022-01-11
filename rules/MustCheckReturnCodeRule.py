from lark import tree
from typing import Set

from output_sarif import *
from rules.FunctionsReturningErrorsGatherer import FunctionsReturningErrorsGatherer
from rules.FunctionCallsGatherer import FunctionCallsGatherer


class MustCheckReturnCodeRule:
    """
    Gather function calls and their return values.
    """

    RULE_TEXT = "This function returns an error code which must be properly checked."
    RULE_NAME = "must-check-error-code"

    def run_rule(self, gathered_data):
        functions_returning_errors = gathered_data[
            FunctionsReturningErrorsGatherer.GATHERER_NAME
        ]
        function_calls = gathered_data[FunctionCallsGatherer.GATHERER_NAME]

        results = []
        for call in function_calls:
            file_name, function_name, returned_list = call

            if function_name in functions_returning_errors:
                idx = functions_returning_errors[function_name]
                must_check = returned_list[idx].children[0]

                positions = (
                    must_check.line,
                    must_check.column,
                    must_check.end_line,
                    must_check.end_column,
                )
                sarif = generic_sarif(
                    file_name,
                    self.RULE_NAME,
                    self.RULE_TEXT,
                    positions,
                )
                results.append(sarif)
        return results
