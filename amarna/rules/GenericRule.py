from lark import Tree, Visitor


class GenericRule(Visitor):
    """
    Generic class for a runnable rule.
    """

    def run_rule(self, fname: str, tree: Tree):
        # TODO (montyly): investigate if this pylint rule should be removed
        # and an __init__ function created
        # pylint: disable=attribute-defined-outside-init
        self.fname = fname
        self.results = []
        self.original_tree = tree
        self.visit(tree)
        return self.results
