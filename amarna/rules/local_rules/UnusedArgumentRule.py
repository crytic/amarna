from typing import Set, Optional, Any
from lark import Tree, Token

from amarna.Result import PositionType, create_result
from amarna.rules.GenericRule import GenericRule


class UnusedArgumentRule(GenericRule):
    """
    Check for unused arguments inside a function
    """

    RULE_TEXT = "Unused arguments might indicate a misspelled variable use or unnecessary argument."
    RULE_NAME = "unused-arguments"

    # visit the code_element_function node of the AST
    def code_element_function(self, tree: Tree) -> None:
        # pylint: disable=too-many-branches

        function_name: Optional[str] = None
        code_block: Optional[Any] = None

        arguments = set()
        for child in tree.children:
            # get the function name
            if child.data == "identifier_def":
                # TODO (montyly): attribute access error
                function_name = child.children[0]  # type: ignore

            # get the arguments names
            elif child.data == "arguments":
                for args in child.find_data("identifier_def"):
                    arguments.add(args.children[0])

            # get the function code ASTree
            elif child.data == "code_block":
                code_block = child

            # ignore if the function is a @storage_var
            elif child.data == "decorator_list":
                for decorator in child.find_data("identifier_def"):
                    # since this is a class attribute, there is no need
                    # to check argument usage because there is no code.
                    if decorator.children[0] == "storage_var":
                        return

        assert function_name
        assert code_block

        # find used identifiers in the function code
        used_ids: Set[Token] = set()
        for code_child in code_block.find_data("identifier"):
            used_ids.add(code_child.children[0])

        unused_arguments = arguments - used_ids
        if not unused_arguments:
            return

        # if NO argument is used, guess that its due to the cast pattern
        # TODO: make precise by checking usage of cast(fp - 2 - STRUCT.SIZE, STRUCT*) and check that
        #       - struct name matches the casted type
        #       - all argument types match the struct types and order
        if len(unused_arguments) == len(arguments) and function_name.endswith("_new"):
            return

        # # gather all hint code and check if the arguments are used there
        # all_hints = ""
        # for hint in self.original_tree.find_data("code_element_hint"):
        #     all_hints += hint.children[0]

        # # remove imports used in hints
        # used_in_hints = set()
        # for unused in unused_arguments:
        #     argument_hint = "ids." + unused.value
        #     if argument_hint in all_hints:
        #         used_in_hints.add(unused)

        # unused_arguments = unused_arguments - used_in_hints

        # find if the current tree is part of a @contract_interface
        # to ignore unused arguments in that case
        structures_namespaces = list(self.original_tree.find_data("code_element_struct")) + list(
            self.original_tree.find_data("code_element_namespace")
        )
        for struct in structures_namespaces:
            for child in struct.find_data("decorator_list"):
                for decorator in child.find_data("identifier_def"):
                    if decorator.children[0] == "contract_interface":
                        if tree in struct.iter_subtrees():
                            return

        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    if decorator in [
                        "event",
                    ]:
                        return

        # report unused arguments
        for arg in sorted(unused_arguments):
            # TODO (montyly): mypy complain about the next attributes accesses
            positions = PositionType(arg.line, arg.column, arg.end_line, arg.end_column)  # type: ignore
            sarif = create_result(
                self.fname,
                self.RULE_NAME,
                self.RULE_TEXT,
                positions,
            )
            self.results.append(sarif)
