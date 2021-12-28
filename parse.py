from typing import Any, Dict
from lark import Lark, tree, Visitor, exceptions
import json
import os

# setup parser
grammar_file = "cairo.lark"
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


def make_png(t):
    tree.pydot__tree_to_png(t, "out.png")


def getPosition(tree: tree.Tree) -> tuple[int, int, int, int]:
    if hasattr(tree, "meta"):
        meta = tree.meta
        return (meta.line, meta.column, meta.end_line, meta.end_column)


def sarif_out(filename: str, tree: tree.Tree) -> Dict[str, Any]:
    start_line, start_col, end_line, end_col = getPosition(tree)
    return {
        "ruleId": f"warn-arith-{tree.data}",
        "level": "warning",
        "message": {
            "text": "arithmetic is defined over finite field and has potential for over/underflows"
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

    def expr_mul(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    def expr_div(self, tree):
        self.results.append(sarif_out(self.fname, tree))

    # def expr_add(self, tree):
    #     self.results.append(sarif_out(self.fname, tree))

    # def expr_sub(self, tree):
    #     self.results.append(sarif_out(self.fname, tree))


def find_arithmetic(filename: str):
    try:
        t = cairo_parser.parse(open(filename, "r").read(), start="cairo_file")
    except exceptions.UnexpectedCharacters as e:
        print(f"Could not parse {filename}: {e}")
        return []
    V = ArithmeticVisitor(filename)
    V.visit(t)
    return V.results


def test_basic():
    fname = "/Users/fcasal/Documents/repos/stark-perpetual/src/services/perpetual/cairo/order/validate_limit_order.cairo"
    find_arithmetic(fname)


def search_directory(rootdir):
    all_results = []
    total = 0
    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)
            if fname.endswith(".cairo"):
                res = find_arithmetic(fname)
                if res:
                    all_results += res

    sarif = {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
        "runs": [{"tool": {"driver": {"name": "Amarna"}}, "results": all_results}],
    }
    open("arithm_warnings.sarif", "w").write(json.dumps(sarif))


rootdir = "/Users/fcasal/Documents/repos/stark-perpetual/src"
search_directory(rootdir)
