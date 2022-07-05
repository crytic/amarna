from collections import defaultdict
from typing import Dict, List
from amarna.Result import ResultMultiplePositions, result_multiple_positions

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import (
    DeclaredFunctionsGatherer,
    FunctionType,
)
from amarna.rules.gatherer_rules.ImportGatherer import ImportGatherer, ImportType


class StorageVarCollisionRule:
    """
    Storage variable is declared multiple times across files.
    """

    RULE_TEXT = "[This](0) storage variable is also declared [here](1), shadowing it and causing both storage variables to always be equal."
    RULE_NAME = "storage-var-collision"

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]

        import_stmts: List[ImportType] = gathered_data[ImportGatherer.GATHERER_NAME]

        results = []
        seen = defaultdict(list)
        for func in declared_functions:
            if "storage_var" in func.decorators:
                seen[(func.file_location, func.name)].append(func)

                files_marked = []
                for imp in import_stmts:
                    # check if there is any import from the location
                    # of the storage variable
                    if func.file_location.endswith(imp.where_imported):
                        # do not flag the same file repeatedly
                        if imp.file_location in files_marked:
                            continue

                        files_marked.append(imp.file_location)
                        seen[(imp.file_location, func.name)].append(func)

        for name in seen:
            if len(seen[name]) > 1:
                sorted_seen = sorted(seen[name], key=lambda x: x.file_location)

                result = result_multiple_positions(
                    [s.file_location for s in sorted_seen],
                    self.RULE_NAME,
                    self.RULE_TEXT,
                    [s.position for s in sorted_seen],
                )
                # do not add findings twice
                if result.position_list not in (r.position_list for r in results):
                    results.append(result)

        return results
