from lark import Lark, tree, Visitor, exceptions
import json
import os

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


def print_child(z):
    if z and hasattr(z, "children"):
        print(z)
        for child in z.children:
            print_child(child)


def make_png(t):
    tree.pydot__tree_to_png(t, "out.png")


# make_png(t)
def getPosition(tree):
    if hasattr(tree, "meta"):
        meta = tree.meta
        return (meta.line, meta.column, meta.end_line, meta.end_column)


def sarif_out(filename, tree):
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

    results = []

    def expr_mul(self, tree):
        self.results.append(sarif_out(self.fname, tree))
        # print(f"mul: {tree}")

    # def expr_sub(self, tree):
    #     self.results.append(sarif_out(self.fname, tree))
        # print(f"sub: {tree}")

    def expr_div(self, tree):
        self.results.append(sarif_out(self.fname, tree))
        # print(f"div: {tree}")

    # def expr_add(self, tree):
    #     self.results.append(sarif_out(self.fname, tree))
        # print(f"add: {tree}")


def find_arithmetic(filename):
    try:
        t = cairo_parser.parse(open(filename, "r").read(), start="cairo_file")
    except exceptions.UnexpectedCharacters:
        return []
    V = ArithmeticVisitor(filename)
    V.visit(t)
    return V.results


def test_basic():
    fname = "/Users/fcasal/Documents/repos/stark-perpetual/src/services/perpetual/cairo/order/validate_limit_order.cairo"

    find_arithmetic(fname)


rootdir = "/Users/fcasal/Documents/repos/stark-perpetual/src"


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
                    total += 1
                    if total > 0:
                        break

    sarif = {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
        "runs": [{"tool": {"driver": {"name": "Amarna"}}, "results": all_results[:20]}],
    }
    open("arithm_warnings.sarif", "w").write(json.dumps(sarif))


search_directory(rootdir)
