from collections import defaultdict
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

    RULE_TEXT = "[This](0) storage variable is also declared [here](1)."
    RULE_NAME = "storage-var-collision"

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]

        results = []
        seen = defaultdict(list)
        for func in declared_functions:
            if "storage_var" in func.decorators:
                seen[func.name].append(func)

        for name in seen:
            if len(seen[name]) > 1:
                for duplicate in seen[name][1:]:
                    result = result_multiple_positions(
                        seen[name][0].file_location,
                        duplicate.file_location,
                        self.RULE_NAME,
                        self.RULE_TEXT,
                        [seen[name][0].position, duplicate.position],
                    )
                    results.append(result)
        return results
