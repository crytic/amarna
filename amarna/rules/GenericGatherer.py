from typing import TypeVar, Generic

from lark import Tree, Visitor

# We need generic typing because classes derived from GenericGatherer
# Will return different types for gather
GenericGatherType = TypeVar("GenericGatherType")


class GenericGatherer(Visitor, Generic[GenericGatherType]):
    """
    Generic class for a rule that gathers data.
    """

    def gather(self, fname: str, tree: Tree) -> GenericGatherType:
        # TODO (montyly): investigate if this pylint rule should be removed
        # and an __init__ function created
        # pylint: disable=attribute-defined-outside-init
        self.fname = fname
        self.results: GenericGatherType = []  # type: ignore
        self.original_tree = tree
        self.visit(tree)
        return self.get_gathered_data()

    def get_gathered_data(self) -> GenericGatherType:
        # Overriden in inherited class
        # TODO (montyly): use abc?
        return self.results
