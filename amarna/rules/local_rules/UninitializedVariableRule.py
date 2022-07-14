import re
from typing import Set

from lark import Tree, Token
from amarna.rules.GenericRule import GenericRule
from amarna.Result import create_result_token


class UninitializedVariableRule(GenericRule):
    """
    Check for uninitialized local variables.
    """

    RULE_TEXT = "This local variable is uninitialized and never assigned."
    RULE_NAME = "uninitialized-variable"

    def code_element_function(self, tree: Tree) -> None:
        local_variables: Set[Token] = set()
        assigned_variables: Set[Token] = set()

        for local_declaration in tree.find_data("code_element_local_var"):
            # only gather unintialized locals
            if len(local_declaration.children) == 1:
                for child in local_declaration.children[0].find_data("identifier_def"):
                    local_variables.add(child.children[0])

        # ignore if they are assigned
        for let_reference in tree.find_data("code_element_reference"):
            for child in let_reference.children[0].find_data("identifier_def"):
                assigned_variables.add(child.children[0])

        # ignore if they are expressed in a inst_assert_eq used as assignment
        for a in tree.find_data("inst_assert_eq"):
            for children_id in a.children[0].find_data("identifier"):
                assigned_variables.add(children_id.children[0])

        # ignore if they are expressed in a assert used as assignment
        for a in tree.find_data("code_element_compound_assert_eq"):
            for b in a.children:
                if b.data == "atom_identifier":
                    assigned_variables.add(b.children[0].children[0])

        uninitialized_locals = local_variables - assigned_variables
        if not uninitialized_locals:
            return

        # gather all hint code and check if the variables are there
        all_hints = ""
        for hint in self.original_tree.find_data("code_element_hint"):
            all_hints += hint.children[0]

        # for now just ignore if they're in a hint
        used_in_hints = set()
        for uninitialized in uninitialized_locals:
            if re.search("ids\." + uninitialized.value + "( |,|\.).*=", all_hints):
                used_in_hints.add(uninitialized)

        uninitialized_locals = uninitialized_locals - used_in_hints

        for tok in uninitialized_locals:
            result = create_result_token(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                tok,
            )
            self.results.append(result)
