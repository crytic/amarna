import os
from pathlib import Path

from amarna.amarna import Amarna, analyze_directory, analyze_file
from amarna.Result import create_summary
from amarna.command_line import filter_results_from_disable

_module_dir = Path(__file__).resolve().parent
TESTS_DIR = _module_dir
TESTS_DIR_STR = str(TESTS_DIR)

def test_all() -> None:
    for subdir, _dirs, files in os.walk(TESTS_DIR):
        if TESTS_DIR_STR == subdir:
            for file in files:
                _test_single(file)

        if subdir.endswith("test"):
            _test_directory(subdir)


def _test_single(filename: str) -> None:
    FILE, ext = os.path.splitext(filename)
    if ext != ".cairo":
        return

    test_file = str(TESTS_DIR.joinpath(FILE + ext))

    all_rules = Amarna.get_all_rule_names()

    results = analyze_file(test_file, all_rules)
    results = filter_results_from_disable(results)

    summary = create_summary(results)

    expected_result = str(TESTS_DIR.joinpath("expected", FILE + ".expected"))
    try:
        with open(expected_result, "r", encoding="utf8") as f:
            expected = f.read()
        assert expected == summary

    except FileNotFoundError as e:
        print("Expected test result does not exist. Creating it.")
        print("at {}".format(expected_result))
        with open(expected_result, "w", encoding="utf8") as f:
            f.write(summary)


def _test_directory(filename: str) -> None:
    if not os.path.isdir(filename):
        return

    test_name = os.path.basename(filename)

    all_rules = Amarna.get_all_rule_names()

    results = analyze_directory(filename, all_rules)
    summary = create_summary(results)

    expected_result = str(TESTS_DIR.joinpath("expected", test_name + ".expected"))
    try:
        with open(expected_result, "r", encoding="utf8") as f:
            expected = f.read()
        assert expected == summary

    except FileNotFoundError as e:
        print("Expected test result does not exist. Creating it.")
        print("at {}".format(expected_result))
        with open(expected_result, "w", encoding="utf8") as f:
            f.write(summary)
