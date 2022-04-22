from dataclasses import dataclass
from typing import List

from lark import Tree
from amarna.rules.GenericGatherer import GenericGatherer
from amarna.Result import token_positions, PositionType


@dataclass
class ImportType:
    """Represents an import statement."""

    import_name: str
    alias_name: str
    where_imported: str
    location: PositionType
    file_location: str


class ImportGatherer(GenericGatherer):
    """
    Gather all import statements.
    """

    GATHERER_NAME = "ImportGatherer"

    def __init__(self) -> None:
        super().__init__()
        self.import_stmts: List[ImportType] = []

    def get_gathered_data(self) -> List[ImportType]:
        return self.import_stmts

    def cairo_file(self, tree: Tree) -> None:
        # iterate over the imports
        for code_imports in tree.find_data("code_element_import"):
            where_imported = ""
            for child in code_imports.children:
                # gather from where it is being imported
                if child.data == "identifier":
                    where_imported = "/".join(map(str, child.children)) + ".cairo"

                # gather what is being imported
                if child.data == "aliased_identifier":
                    assert where_imported
                    # this is just a simple import
                    if len(child.children) == 1:
                        import_name = child.children[0].children[0]
                        stmt = ImportType(
                            str(import_name),
                            "",
                            where_imported,
                            token_positions(import_name),
                            self.fname,
                        )
                        self.import_stmts.append(stmt)

                    # this is an aliased import import XX as YY, we keep the new name
                    elif len(child.children) == 2:
                        import_name = child.children[0].children[0]
                        alias_name = child.children[1].children[0]

                        stmt = ImportType(
                            str(import_name),
                            alias_name,
                            where_imported,
                            token_positions(import_name),
                            self.fname,
                        )
                        self.import_stmts.append(stmt)
