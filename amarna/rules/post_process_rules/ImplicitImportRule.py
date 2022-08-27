from typing import Dict, List
from amarna.Result import ResultMultiplePositions, result_multiple_positions

from amarna.rules.gatherer_rules.DeclaredFunctionsGatherer import (
    DeclaredFunctionsGatherer,
    FunctionType,
)
from amarna.rules.gatherer_rules.ImportGatherer import ImportGatherer, ImportType


class ImplicitImportRule:
    """
    External, view and l1_handler declared functions will be imported even if not explicitly imported.
    """

    RULE_TEXT = "[This](0) function will be imported by [here](1), even though it was not explicitly imported."
    RULE_NAME = "implicit-import"

    DECORATORS = ["external", "view", "l1_handler"]

    def run_rule(self, gathered_data: Dict) -> List[ResultMultiplePositions]:
        declared_functions: List[FunctionType] = gathered_data[
            DeclaredFunctionsGatherer.GATHERER_NAME
        ]

        import_stmts: List[ImportType] = gathered_data[ImportGatherer.GATHERER_NAME]

        results = []

        for func in declared_functions:
            if any(decorator in self.DECORATORS for decorator in func.decorators):

                explicitly_imp: List[ImportType] = []
                explicitly_import_names: List[str] = []
                for imp in import_stmts:
                    # gather all explicitly imported functions
                    # from the location of the external function
                    if func.file_location.endswith(imp.where_imported):
                        explicitly_import_names.append(imp.import_name)
                        explicitly_imp.append(imp)

                # check if there was any import and that it was not
                # explicitly imported
                if explicitly_imp and func.name not in explicitly_import_names:
                    imp = explicitly_imp[0]
                    result = result_multiple_positions(
                        [func.file_location, imp.file_location],
                        self.RULE_NAME,
                        self.RULE_TEXT,
                        [func.position, imp.location],
                    )
                    results.append(result)

        return results
