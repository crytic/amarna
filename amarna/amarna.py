import inspect
import os
from typing import Any, List, Dict, Union
from pathlib import Path
from lark import Lark, Tree, tree, exceptions
from amarna.Result import Result, ResultMultiplePositions

from amarna.rules import gatherer_rules_module, local_rules_module, post_process_rules_module
from amarna.rules.GenericRule import GenericRule


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

    @staticmethod
    def get_all_rule_names() -> List[str]:
        return list(
            map(
                lambda x: x.RULE_NAME,
                Amarna.load_classes_in_module(local_rules_module)
                + Amarna.load_classes_in_module(post_process_rules_module),
            )
        )

    @staticmethod
    def print_rule_names_and_descriptions() -> List[str]:
        ruleset = Amarna.load_classes_in_module(local_rules_module) + Amarna.load_classes_in_module(
            post_process_rules_module
        )
        for rule in ruleset:
            print(rule.RULE_NAME)

    def __init__(self, only_these_analysis_rules: List[str]) -> None:
        """
        Load Cairo grammar and analysis rules.
        """
        self.parser = Amarna.load_cairo_grammar()
        # self.data maps the gather name to the value returned by
        # the different "gather" functions
        # Which return a GenericGatherType type (python generic)
        self.data: Dict[str, Any] = {}
        self.rules: List[GenericRule] = [
            rule
            for rule in Amarna.load_classes_in_module(local_rules_module)
            if rule.RULE_NAME in only_these_analysis_rules
        ]
        self.post_process_rules = [
            rule
            for rule in Amarna.load_classes_in_module(post_process_rules_module)
            if rule.RULE_NAME in only_these_analysis_rules
        ]
        self.gatherers = Amarna.load_classes_in_module(gatherer_rules_module)

    def run_local_rules(
        self, filename: str, parsed_cairo_file: Any, png: bool = False
    ) -> List[Union[Result, ResultMultiplePositions]]:
        """
        Run all local rules.

        """
        if png:
            png_filename = os.path.basename(filename).split(".")[0] + ".png"
            make_png(parsed_cairo_file, png_filename)

        results = []
        for Rule in self.rules:
            results += Rule.run_rule(filename, parsed_cairo_file)

        return results

    def run_gatherer_rules(self, filename: str, parsed_cairo_file: Tree) -> None:
        """
        Run all gatherer rules.
        """
        for Gatherer in self.gatherers:
            self.data[Gatherer.GATHERER_NAME] = Gatherer.gather(filename, parsed_cairo_file)

    def run_post_process_rules(self) -> List[Union[Result, ResultMultiplePositions]]:
        """
        Run all post-processing rules.
        """
        results = []
        for Rule in self.post_process_rules:
            results += Rule.run_rule(self.data)
        return results

    def parse_cairo_file(self, filename: str) -> Union[Tree, None]:
        """
        Parse the cairo file
        """
        try:
            with open(filename, "r", encoding="utf8") as f:
                # the cairo grammar requires a newline at the end
                return self.parser.parse(f.read() + "\n", start="cairo_file")
        except (exceptions.UnexpectedCharacters, exceptions.UnexpectedToken) as e:
            print(f"Could not parse {filename}: {e}")
            return None


def analyze_directory(rootdir: str, rule_names: List[str]) -> List[Any]:
    """
    Run rules in all .cairo files inside a directory.
    """
    amarna = Amarna(rule_names)

    all_results = []
    run_gather = False

    for subdir, _dirs, files in os.walk(rootdir):
        for file in files:
            fname = os.path.join(subdir, file)

            if fname.endswith(".cairo"):
                parsed_cairo_file = amarna.parse_cairo_file(fname)
                if not parsed_cairo_file:
                    continue

                all_results += amarna.run_local_rules(fname, parsed_cairo_file)
                amarna.run_gatherer_rules(fname, parsed_cairo_file)
                run_gather = True

    if run_gather:
        all_results += amarna.run_post_process_rules()
    else:
        print(f"Could not find any cairo files in {rootdir}")
    return sorted(all_results, key=lambda x: x.to_summary())


def analyze_file(
    fname: str, rules_names: List[str], png: bool = False
) -> List[Union[Result, ResultMultiplePositions]]:
    """
    Run analysis rules on a .cairo file.
    """
    amarna = Amarna(rules_names)
    all_results = []
    parsed_cairo_file = amarna.parse_cairo_file(fname)
    if parsed_cairo_file:
        all_results += amarna.run_local_rules(fname, parsed_cairo_file, png)
        amarna.run_gatherer_rules(fname, parsed_cairo_file)
        all_results += amarna.run_post_process_rules()
    return sorted(all_results, key=lambda x: x.to_summary())


if __name__ == "__main__":
    pass
