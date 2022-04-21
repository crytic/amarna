from lark import Tree

from amarna.rules.GenericRule import GenericRule
from amarna.Result import PositionType, create_result


class UnknownDecoratorRule(GenericRule):
    """
    Check for misspelled function decorators.
    """

    RULE_TEXT = "Unknown of misspelled function decorator."
    RULE_NAME = "unknown-decorator"

    known_decorators = [
        "storage_var",
        "external",
        "view",
        "constructor",
        "l1_handler",
        "known_ap_change",
        "event",
        "raw_input",
        "raw_output",
    ]

    def code_element_function(self, tree: Tree) -> None:
        unknown_decorators = []
        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    if decorator not in self.known_decorators:
                        unknown_decorators.append(decorator)

        for arg in unknown_decorators:
            # TODO (montyly): mypy compain about the next attributes access
            positions = PositionType(arg.line, arg.column, arg.end_line, arg.end_column)  # type: ignore
            sarif = create_result(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
