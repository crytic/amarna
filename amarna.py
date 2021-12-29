from typing import Any, Dict, List
from lark import Lark, tree, Visitor, exceptions
import os


def make_png(t: tree.Tree, out_name: str):
    tree.pydot__tree_to_png(t, out_name)


def getPosition(tree: tree.Tree) -> tuple[int, int, int, int]:
    if hasattr(tree, "meta"):
        meta = tree.meta
        return (meta.line, meta.column, meta.end_line, meta.end_column)


def sarif_out(filename: str, tree: tree.Tree) -> Dict[str, Any]:
    start_line, start_col, end_line, end_col = getPosition(tree)
    return {
        "ruleId": f"arithmetic-{tree.data}",
        "level": "warning",
        "message": {
            "text": "Cairo arithmetic is defined over a finite field and has potential for overflows."
        },
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": {
                        "startLine": start_line,
                        "startColumn": start_col,
                        "endLine": end_line,
                        "endColumn": end_col,
                    },
                }
            }
        ],
    }


class ArithmeticVisitor(Visitor):
    """
    Visit arithmetic nodes
    """

    def __init__(self, fname) -> None:
        super().__init__()
        self.fname = fname
        self.results = []

    def get_results(self):
        return self.results

    def expr_mul(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    def expr_div(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    def expr_add(self, tree: tree.Tree):
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        self.results.append(sarif_out(self.fname, tree))

    def expr_sub(self, tree: tree.Tree):
        # ignore adding to registers
        if tree.children[0].data == "atom_reg":
            return

        self.results.append(sarif_out(self.fname, tree))


class Amarna:
    @staticmethod
    def load_cairo_grammar():
        grammar_file = "grammars/cairo.lark"
        cairo_parser = Lark(
            open(grammar_file, "r").read(),
            start=[
                "cairo_file",
                "code_block",
                "code_element",
                "expr",
                "instruction",
                "type",
                "typed_identifier",
            ],
            parser="lalr",
            propagate_positions=True,
        )

        return cairo_parser

    def __init__(self):
        self.parser = Amarna.load_cairo_grammar()

    def find_arithmetic(self, filename: str):
        try:
            t = self.parser.parse(open(filename, "r").read(), start="cairo_file")
        except exceptions.UnexpectedCharacters as e:
            print(f"Could not parse {filename}: {e}")
            return []

        V = ArithmeticVisitor(filename)
        V.visit(t)
        return V.get_results()


def test_basic():
    amarna = Amarna()

    fname = "/Users/fcasal/Documents/repos/stark-perpetual/src/services/perpetual/cairo/order/validate_limit_order.cairo"
    amarna.find_arithmetic(fname)


def analyze_directory(rootdir: str) -> List[Any]:
    amarna = Amarna()

    all_results = []

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)

            if fname.endswith(".cairo"):
                res = amarna.find_arithmetic(fname)
                if res:
                    all_results += res
    return all_results


def analyze_file(fname: str) -> List[Any]:
    amarna = Amarna()

    return amarna.find_arithmetic(fname)


############################
# dangerous cairo patterns #
############################
# using ap and fp registers manually
# call and jmp and revoked references
# undefined behavior when using [ap] directly
# callback before tempvars
