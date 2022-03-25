from lark import tree, Visitor


class GenericGatherer(Visitor):
    """
    Generic class for a rule that gathers data.
    """

    def gather(self, fname: str, tree: tree.Tree):
        self.fname = fname
        self.results = []
        self.visit(tree)
        return self.get_gathered_data()
