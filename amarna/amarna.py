from typing import Any, List
from lark import Lark, tree, exceptions
import os

from amarna.rules import all_rules_module, post_process_rules_module, all_gatherers_module
import inspect


def make_png(t: tree.Tree, out_name: str):
    """
    Creates a PNG of the AST in the out_name file
    """
    tree.pydot__tree_to_png(t, out_name)


class Amarna:
    """
    The main class -- loads the cairo grammar, and runs rules.
    """

    @staticmethod
    def load_cairo_grammar():
        grammar_file = "./amarna/grammars/cairo.lark"
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

    @staticmethod
    def load_classes_in_module(module):
        return [cls() for (_, cls) in inspect.getmembers(module, inspect.isclass)]

    def __init__(self):
        """
        Load Cairo grammar and analysis rules.
        """
        self.parser = Amarna.load_cairo_grammar()
        self.data = {}
        self.rules = Amarna.load_classes_in_module(all_rules_module)
        self.post_process_rules = Amarna.load_classes_in_module(
            post_process_rules_module
        )
        self.gatherers = Amarna.load_classes_in_module(all_gatherers_module)

    def run_rules(self, filename: str, png: bool = False):
        """
        Run all rules.

        TODO: add argument to only run certain rule or exclude others.
        """
        # parse the cairo file
        try:
            t = self.parser.parse(open(filename, "r").read(), start="cairo_file")
        except exceptions.UnexpectedCharacters as e:
            print(f"Could not parse {filename}: {e}")
            return []

        if png:
            png_filename = os.path.basename(filename).split(".")[0] + ".png"
            make_png(t, png_filename)

        results = []
        for Rule in self.rules:
            results += Rule.run_rule(filename, t)

        for Gatherer in self.gatherers:
            self.data[Gatherer.GATHERER_NAME] = Gatherer.gather(filename, t)

        return results

    def run_post_process_rules(self):
        results = []
        for Rule in self.post_process_rules:
            results += Rule.run_rule(self.data)
        return results


def analyze_directory(rootdir: str) -> List[Any]:
    """
    Run rules in all .cairo files inside a directory.
    """
    amarna = Amarna()

    all_results = []

    for subdir, dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)

            if fname.endswith(".cairo"):
                res = amarna.run_rules(fname)
                if res:
                    all_results += res

    all_results += amarna.run_post_process_rules()
    return all_results


def analyze_file(fname: str, png: bool = False) -> List[Any]:
    """
    Run analysis rules on a .cairo file.
    """
    amarna = Amarna()

    return amarna.run_rules(fname, png)


if __name__ == "__main__":
    pass
