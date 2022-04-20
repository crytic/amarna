import os
import argparse
from amarna.amarna import analyze_directory, analyze_file
from amarna.Result import Result, ResultMultiplePositions, output_result
from amarna.Result import SARIF_MODE, SUMMARY_MODE
from typing import Optional, List, Union

example_usage = """---------------\nUsage examples\n---------------
Analyze a Cairo project in the current directory and export results to a file:
 amarna . -o out.sarif

Analyze a single file `deleverage.cairo` and export results to a file:
 amarna deleverage.cairo -o deleverage.sarif

Analyze a single file `code.cairo` and print a summary of the results:
 amarna code.cairo -s

Parse a Cairo file and output the recovered AST in `png`:
 amarna file.cairo -png"""


def main() -> None:

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
    )

    parser.add_argument("-p", "--print", action="store_true", help="print output")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="file to write the output results in sarif format",
    )

    parser.add_argument("-summary", "--summary", action="store_true", help="output summary")

    parser.add_argument(
        "-png", "--png", action="store_true", help="save a png with the AST of a file"
    )

    args = parser.parse_args()
    filename = args.filename

    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)

    results: List[Union[Result, ResultMultiplePositions]]
    if os.path.isdir(filename):
        results = analyze_directory(filename)
    else:
        results = analyze_file(filename, png=args.png)

    mode = SARIF_MODE
    if args.summary:
        args.print = True
        mode = SUMMARY_MODE

    if args.output or args.print:
        output_result(results, args.output, args.print, mode)


if __name__ == "__main__":
    main()
