from typing import List, Set
from lark import Tree, Token
from amarna.Result import PositionType, create_result

from amarna.rules.GenericRule import GenericRule


class UnusedImportRule(GenericRule):
    """
    Check for unused imports.
    """

    RULE_TEXT = "Unused imports could be removed."
    RULE_NAME = "unused-imports"

    # visit the whole cairo_file node of the AST
    def cairo_file(self, tree: Tree) -> None:
        # pylint: disable=too-many-locals,too-many-branches

        imports = set()
        # iterate over the imports
        for code_imports in tree.find_data("code_element_import"):
            for child in code_imports.children:

                if child.data == "aliased_identifier":

                    # this is just a simple import
                    if len(child.children) == 1:
                        child_id = child.children[0].children[0]
                        if child_id in imports:
                            print("double import of ", child_id)
                        imports.add(child_id)

                    # this is an aliased import import XX as YY, we keep the new name
                    elif len(child.children) == 2:
                        child_id = child.children[1].children[0]
                        if child_id in imports:
                            print("double import of ", child_id)
                        imports.add(child.children[1].children[0])

        used_ids: Set[Token] = set()
        # gather identifiers used in the code
        for function_code in self.original_tree.find_data("code_element_function"):
            for code_child in function_code.find_data("identifier"):
                # TODO (montyly): attribute access error
                used_ids.add(code_child.children[0])  # type: ignore

        # gather types used in struct declaractions
        for struct_declration in self.original_tree.find_data("code_element_struct"):
            for code_child in struct_declration.find_data("identifier"):
                # TODO (montyly): attribute access error
                used_ids.add(code_child.children[0])  # type: ignore

        unused_imports = imports - used_ids
        if not unused_imports:
            return

        # gather all hint code and check if the imports are there
        all_hints: List[str] = []
        for hint in self.original_tree.find_data("code_element_hint"):
            all_hints.append(hint.children[0])

        hints_str = "\n".join(all_hints)

        # remove imports used in hints
        used_in_hints = set()
        for unused in unused_imports:
            if unused.value in hints_str:
                used_in_hints.add(unused)

        unused_imports = unused_imports - used_in_hints

        # report unused imports
        for arg in sorted(unused_imports):
            # print(f"\t{arg.value} imported at line {arg.line}")
            positions = PositionType(arg.line, arg.column, arg.end_line, arg.end_column)  # type: ignore
            sarif = create_result(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
