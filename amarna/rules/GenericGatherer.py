from lark import Tree, Visitor


class GenericGatherer(Visitor):
    """
    Generic class for a rule that gathers data.
    """

    def gather(self, fname: str, tree: Tree):
        # TODO (montyly): investigate if this pylint rule should be removed
        # and an __init__ function created
        # pylint: disable=attribute-defined-outside-init
        self.fname = fname
        self.results = []
        self.visit(tree)
        return self.get_gathered_data()

    def get_gathered_data(self):
        # Overriden in inherited class
        # TODO (montyly): use abc?
        pass
