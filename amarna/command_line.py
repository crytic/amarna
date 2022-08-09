import os
import argparse
from amarna.amarna import Amarna, analyze_directory, analyze_file
from amarna.Result import Result, ResultMultiplePositions, output_result
from amarna.Result import SARIF_MODE, SUMMARY_MODE
from typing import List, Union, Dict
import sys

example_usage = """---------------\nUsage examples\n---------------
Analyze a Cairo project in the current directory and export results to a file:
 amarna . -o out.sarif

Analyze a single file `deleverage.cairo` and export results to a file:
 amarna deleverage.cairo -o deleverage.sarif

Analyze a single file `code.cairo` and print a summary of the results:
 amarna code.cairo -s

Parse a Cairo file and output the recovered AST in `png`:
 amarna file.cairo -png

Parse a Cairo file and only run the unused_import rule:
 amarna file.cairo --rules=unused-imports

Analyze a Cairo file using all rules except the arithmetic-add rule:
 amarna file.cairo --except-rules=arithmetic-add
 """


def parse_comma_sep_strings(s: str) -> List[str]:
    if s:
        return [token.strip() for token in s.split(",") if token.strip()]
    else:
        return []


def get_rule_names(rule_str: str, excluded_str: str) -> List[str]:
    ALL_RULES = Amarna.get_all_rule_names()

    rules = parse_comma_sep_strings(rule_str)
    excluded = parse_comma_sep_strings(excluded_str)

    for rule in rules + excluded:
        if rule not in ALL_RULES:
            print("Unknown rule: " + repr(rule))
            sys.exit(-1)

    if rules:
        base_rules = rules
    else:
        base_rules = ALL_RULES

    return [rule for rule in base_rules if rule not in excluded]


def filter_results_from_disable(
    results: List[Union[Result, ResultMultiplePositions]]
) -> List[Union[Result, ResultMultiplePositions]]:
    first_lines_per_file: Dict[str, str] = {}
    disable_token = "# amarna: disable="

    new_results = []
    for result in results:
        if isinstance(result, Result):
            filename = result.filename
        elif isinstance(result, ResultMultiplePositions):
            filename = result.filenames[0]
        if filename in first_lines_per_file:
            first_line = first_lines_per_file[filename]
        else:
            with open(filename, "r", encoding="utf8") as f:
                first_line = f.readline().strip()
                first_lines_per_file[filename] = first_line

        if not first_line.startswith(disable_token):
            new_results.append(result)
            continue

        rule_tok = first_line.split(disable_token)[1]
        rule_list = get_rule_names("", rule_tok)

        if result.rule_name in rule_list:
            new_results.append(result)

    return new_results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Amarna is a static-analyzer for the Cairo programming language.",
        epilog=example_usage,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "filename",
        metavar="-f",
        type=str,
        help="the name of the .cairo file or directory with .cairo files to analyze",
        nargs="?",
    )

    parser.add_argument("-p", "--print", action="store_true", help="print output")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="file to write the output results in sarif format",
    )

    parser.add_argument("-s", "-summary", "--summary", action="store_true", help="output summary")

    parser.add_argument(
        "-png", "--png", action="store_true", help="save a png with the AST of a file"
    )

    parser.add_argument(
        "-rules",
        "--rules",
        type=str,
        help="Only run this set of rules. Enter rule names comma-separated, e.g., dead-store,unused-arguments",
    )

    parser.add_argument(
        "-exclude-rules",
        "--exclude-rules",
        type=str,
        help="Exclude these rules from the analysis. Enter rule names comma-separated, e.g., dead-store,unused-arguments",
    )

    parser.add_argument(
        "-show-rules",
        "--show-rules",
        action="store_true",
        help="Show all supported rules and descriptions.",
    )

    parser.add_argument(
        "-disable-inline",
        "--disable-inline",
        action="store_true",
        help="Disable rules with inline comments. The comments should be the first line and of the form: # amarna: disable=rulename1,rulename2",
    )

    args = parser.parse_args()

    if args.show_rules:
        Amarna.print_rule_names_and_descriptions()
        return 1

    filename = args.filename

    if filename is None:
        print("No file specified")
        return -1

    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)

    if not os.path.exists(filename):
        print(f"The specified file doesn't exist: {filename}")
        return -1

    rule_set_names: List[str] = get_rule_names(args.rules, args.exclude_rules)

    results: List[Union[Result, ResultMultiplePositions]]
    if os.path.isdir(filename):
        results = analyze_directory(filename, rule_set_names)
    else:
        results = analyze_file(filename, rule_set_names, png=args.png)

    if args.disable_inline:
        results = filter_results_from_disable(results)

    mode = SARIF_MODE
    if args.summary:
        args.print = True
        mode = SUMMARY_MODE

    if args.output or args.print:
        output_result(results, args.output, args.print, mode)

    return 0


if __name__ == "__main__":
    main()
