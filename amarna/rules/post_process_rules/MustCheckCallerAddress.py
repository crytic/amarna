from amarna.output_sarif import *

from amarna.rules.gatherer_rules.RValueFunctionCallsGatherer import (
    RValueFunctionCallsGatherer,
)


class MustCheckCallerAddress:
    """
    Gather function calls to get_caller_address.
    """

    RULE_TEXT = "The function get_caller_address returns 0 when the contract is called directly which might be unexpected"
    IGNORED_RULE_TEXT = "The result of get_caller_address is ignored."

    RULE_NAME = "must-check-caller-address"

    # dictionary with function_name : index of the caller address
    TARGET_FUNCTION = {"get_caller_address": 0}

    def run_rule(self, gathered_data):

        function_calls = gathered_data[RValueFunctionCallsGatherer.GATHERER_NAME]

        results = []
        for call in function_calls:
            file_name, function_name, returned_list = call

            if function_name in self.TARGET_FUNCTION:
                idx = self.TARGET_FUNCTION[function_name]

                must_check = returned_list[idx].children[0]

                if must_check == "_":
                    # the caller address is being ignored
                    rule = self.IGNORED_RULE_TEXT
                else:
                    # here we say that it must be checked
                    rule = self.RULE_TEXT

                sarif = generic_sarif_token(
                    file_name,
                    self.RULE_NAME,
                    rule,
                    must_check,
                )
                results.append(sarif)

        return results
