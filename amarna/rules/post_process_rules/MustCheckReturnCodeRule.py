from typing import Dict, Any, List

from amarna.output_sarif import generic_sarif_token
from amarna.rules.gatherer_rules.FunctionsReturningErrorsGatherer import (
    FunctionsReturningErrorsGatherer,
)
from amarna.rules.gatherer_rules.RValueFunctionCallsGatherer import RValueFunctionCallsGatherer

# pylint: disable=too-few-public-methods
class MustCheckReturnCodeRule:
    """
    Gather function calls and their return values.
    """

    RULE_TEXT = "This function returns an error code which must be properly checked."
    RULE_NAME = "must-check-error-code"

    def run_rule(self, gathered_data: Dict) -> List[Dict[str, Any]]:
        functions_returning_errors = gathered_data[FunctionsReturningErrorsGatherer.GATHERER_NAME]
        function_calls = gathered_data[RValueFunctionCallsGatherer.GATHERER_NAME]

        results = []
        for call in function_calls:
            file_name, function_name, returned_list = call

            # when the function is one of those returning errors
            if function_name in functions_returning_errors:
                idx = functions_returning_errors[function_name]
                must_check = returned_list[idx].children[0]

                sarif = generic_sarif_token(
                    file_name,
                    self.RULE_NAME,
                    self.RULE_TEXT,
                    must_check,
                )
                results.append(sarif)

            # also check if returned values were named success or exists
            else:
                for return_name in returned_list:
                    token = return_name.children[0]
                    if token in ["success", "exists"]:

                        sarif = generic_sarif_token(
                            file_name,
                            "sucess-must-be-checked",
                            self.RULE_TEXT,
                            token,
                        )
                        results.append(sarif)

        return results
