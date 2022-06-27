from lark import Tree, Token
from amarna.rules.GenericRule import GenericRule
from amarna.Result import create_result_token, getPosition


class UnenforcedViewRule(GenericRule):
    """
    Find state modifications in functions with @view decorator.
    """

    RULE_TEXT = "This function modifies state but is declared @view."
    RULE_NAME = "unenforced-view"

    def code_element_function(self, tree: Tree) -> None:

        decorators = []
        for child in tree.children:
            if child.data == "decorator_list":
                for args in child.find_data("identifier_def"):
                    decorator = args.children[0]
                    decorators.append(str(decorator))

        if "view" not in decorators:
            return

        for function_call in tree.find_data("function_call"):
            
            for args in function_call.find_data("identifier"):
                if len(args.children) > 1:
                    if str(args.children[1]) == "write":
                        sarif = create_result_token(
                            self.fname,
                            self.RULE_NAME,
                            self.RULE_TEXT,
                            args.children[1],
                        )
                        if sarif in self.results:
                            continue
                        self.results.append(sarif)
