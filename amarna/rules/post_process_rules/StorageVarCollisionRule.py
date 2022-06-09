from typing import Dict, List
from amarna.Result import ResultMultiplePositions, result_multiple_positions

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import (
    DeclaredFunctionsGatherer,
    FunctionType,
)


class StorageVarCollisionRule:
    """
    Storage variable is declared multiple times across files.
    """

    RULE_TEXT = "[This](0) storage variable will is also declared [here](1)."
    RULE_NAME = "storage-var-collision"

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]

        results = []

        storage_vars = filter(lambda func: "storage_var" in func.decorators, declared_functions)

        for func in storage_vars:
            for other_func in storage_vars:

                # do not flag the same declaration
                if other_func == func:
                    continue

                if func.name == other_func.name:
                    result = result_multiple_positions(
                        func.file_location,
                        other_func.file_location,
                        self.RULE_NAME,
                        self.RULE_TEXT,
                        [func.position, other_func.position],
                    )
                    results.append(result)

        return results
