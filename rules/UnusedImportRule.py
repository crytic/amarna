from lark import tree, Token
from typing import Set

from output_sarif import *
from rules.GenericRule import GenericRule


class UnusedImportRule(GenericRule):
    """
    Check for unused imports.
    """

    RULE_TEXT = "Unused imports could be removed."
    RULE_NAME = "unused-imports"

    # visit the whole cairo_file node of the AST
    def cairo_file(self, tree: tree.Tree):

        imports = set()
        # iterate over the imports
        for code_imports in tree.find_data("code_element_import"):
            for child in code_imports.children:

                if child.data == "aliased_identifier":

                    # this is just a simple import
                    if len(child.children) == 1:
                        id = child.children[0].children[0]
                        if id in imports:
                            print("double import of ", id)
                        imports.add(id)

                    # this is an aliased import import XX as YY, we keep the new name
                    elif len(child.children) == 2:
                        id = child.children[1].children[0]
                        if id in imports:
                            print("double import of ", id)
                        imports.add(child.children[1].children[0])

        used_ids: Set[Token] = set()
        # gather identifiers used in the code
        for function_code in self.original_tree.find_data("code_element_function"):
            for code_child in function_code.find_data("identifier"):
                used_ids.add(code_child.children[0])

        # gather types used in struct declaractions
        for struct_declration in self.original_tree.find_data("code_element_struct"):
            for code_child in struct_declration.find_data("identifier"):
                used_ids.add(code_child.children[0])

        unused_imports = imports - used_ids
        if not unused_imports:
            return

        # gather all hint code and check if the imports are there
        all_hints = ""
        for hint in self.original_tree.find_data("code_element_hint"):
            all_hints += hint.children[0]

        # remove imports used in hints
        used_in_hints = set()
        for unused in unused_imports:
            if unused.value in all_hints:
                used_in_hints.add(unused)

        unused_imports = unused_imports - used_in_hints

        # report unused imports
        for arg in unused_imports:
            positions = (arg.line, arg.column, arg.end_line, arg.end_column)
            sarif = generic_sarif(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
