import inspect
import os
from typing import Any, List, Dict
from pathlib import Path
from lark import Lark, tree, exceptions

from amarna.rules import all_rules_module, post_process_rules_module, all_gatherers_module


def make_png(t: tree.Tree, out_name: str) -> None:
    """
    Creates a PNG of the AST in the out_name file
    """
    tree.pydot__tree_to_png(t, out_name)


class Amarna:
    """
    The main class -- loads the cairo grammar, and runs rules.
    """

    @staticmethod
    def load_cairo_grammar() -> Lark:
        _module_dir = Path(__file__).resolve().parent
        GRAMMAR_FILENAME = _module_dir.joinpath("grammars", "cairo.lark")
        with open(GRAMMAR_FILENAME, "r", encoding="utf8") as f:
            buf = f.read()
        cairo_parser = Lark(
            buf,
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
    def load_classes_in_module(module: Any) -> List:
        return [cls() for (_, cls) in inspect.getmembers(module, inspect.isclass)]

    def __init__(self) -> None:
        """
        Load Cairo grammar and analysis rules.
        """
        self.parser = Amarna.load_cairo_grammar()
        # self.data maps the gather name to the value returned by
        # the different "gather" functions
        # Which return a GenericGatherType type (python generic)
        self.data: Dict[str, Any] = {}
        self.rules = Amarna.load_classes_in_module(all_rules_module)
        self.post_process_rules = Amarna.load_classes_in_module(post_process_rules_module)
        self.gatherers = Amarna.load_classes_in_module(all_gatherers_module)

    def run_local_rules(
        self, filename: str, parsed_cairo_file: Any, png: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run all local rules.

        TODO: add argument to only run certain rule or exclude others.
        """
        if png:
            png_filename = os.path.basename(filename).split(".")[0] + ".png"
            make_png(parsed_cairo_file, png_filename)

        results: List[Dict[str, Any]] = []
        for Rule in self.rules:
            results += Rule.run_rule(filename, parsed_cairo_file)

        return results

    def run_gatherer_rules(self, filename, parsed_cairo_file) -> None:
        """
        Run all gatherer rules.
        """
        for Gatherer in self.gatherers:
            self.data[Gatherer.GATHERER_NAME] = Gatherer.gather(filename, parsed_cairo_file)

    def run_post_process_rules(self) -> List[Dict[str, Any]]:
        """
        Run all post-processing rules.
        """
        results = []
        for Rule in self.post_process_rules:
            results += Rule.run_rule(self.data)
        return results

    def parse_cairo_file(self, filename: str):
        """
        Parse the cairo file
        """
        try:
            with open(filename, "r", encoding="utf8") as f:
                return self.parser.parse(f.read(), start="cairo_file")
        except exceptions.UnexpectedCharacters as e:
            print(f"Could not parse {filename}: {e}")
            return None


def analyze_directory(rootdir: str) -> List[Any]:
    """
    Run rules in all .cairo files inside a directory.
    """
    amarna = Amarna()

    all_results = []

    for subdir, _dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)

            if fname.endswith(".cairo"):
                parsed_cairo_file = amarna.parse_cairo_file(fname)
                if not parsed_cairo_file:
                    continue

                all_results += amarna.run_local_rules(fname, parsed_cairo_file)
                amarna.run_gatherer_rules(fname, parsed_cairo_file)

    all_results += amarna.run_post_process_rules()
    return all_results


def analyze_file(fname: str, png: bool = False) -> List[Any]:
    """
    Run analysis rules on a .cairo file.
    """
    amarna = Amarna()

    return amarna.run_local_rules(fname, png)


if __name__ == "__main__":
    pass
