from lark import tree, Visitor


class GenericRule(Visitor):
    """
    Generic class for a runnable rule.
    """

    def run_rule(self, fname: str, tree: tree.Tree):
        self.fname = fname
        self.results = []
        self.visit(tree)
        return self.results

    def get_results(self):
        return self.results
