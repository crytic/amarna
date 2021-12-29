import argparse
from amarna import *
from output_sarif import *


def main():
    parser = argparse.ArgumentParser(description="Analyze Cairo programs!")
    parser.add_argument(
        "filename",
        metavar="-f",
        type=str,
        help="the name of the .cairo file or directory with .cairo files to analyze",
    )

    parser.add_argument("-p", "--print", action="store_true")

    parser.add_argument(
        "-o", "--output", type=str, help="file to write the output results in sarif format"
    )

    args = parser.parse_args()
    filename = args.filename

    if not os.path.isabs(filename):
        filename = os.path.join(os.getcwd(), filename)

    if os.path.isdir(filename):
        results = analyze_directory(filename)
    else:
        results = analyze_file(filename)

    if args.output:
        create_sarif(results, args.output, args.print)


def test_dir():
    rootdir = "/Users/fcasal/Documents/repos/stark-perpetual/src"
    results = analyze_directory(rootdir)
    create_sarif(results, "arithm_warnings.sarif")


if __name__ == "__main__":
    main()
