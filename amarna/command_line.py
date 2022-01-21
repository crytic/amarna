import argparse
from amarna.amarna import analyze_directory, analyze_file
from amarna.output_sarif import *


def main():
    parser = argparse.ArgumentParser(description="Analyze Cairo programs!")
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

    parser.add_argument(
        "-png", "--png", action="store_true", help="save a png with the AST of a file"
    )

    args = parser.parse_args()
    filename = args.filename

    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)

    if os.path.isdir(filename):
        results = analyze_directory(filename)
    else:
        results = analyze_file(filename, args.png)

    if args.output or args.print:
        create_sarif(results, args.output, args.print)


if __name__ == "__main__":
    main()