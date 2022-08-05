import os
from pathlib import Path
import json
from typing import List, Union

from amarna.amarna import Amarna, analyze_directory, analyze_file
from amarna.Result import Result, ResultMultiplePositions, create_summary, create_sarif
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


def load_sarif(results: List[Union[Result, ResultMultiplePositions]]) -> None:
    """
    Loads a sarif str with json.loads to test if generation worked.
    """
    sarif_str = create_sarif(results, None, False)

    try:
        json.loads(sarif_str)
    except json.JSONDecodeError as e:
        assert False, "Sarif generation is broken."


def compare_expected(summary_results: str, expected_filename: str) -> None:
    """
    Compares the obtained summary results with the ones saved in the .expected files.
    If the expected file does not exist, create it with the current summary_results.
    """
    expected_result = str(TESTS_DIR.joinpath("expected", expected_filename + ".expected"))
    try:
        with open(expected_result, "r", encoding="utf8") as f:
            expected = f.read()
        assert expected == summary_results

    except FileNotFoundError as e:
        print("Expected test result does not exist. Creating it.")
        print("at {}".format(expected_result))
        with open(expected_result, "w", encoding="utf8") as f:
            f.write(summary_results)


def _test_single(filename: str) -> None:
    FILE, ext = os.path.splitext(filename)
    if ext != ".cairo":
        return

    test_file = str(TESTS_DIR.joinpath(FILE + ext))

    all_rules = Amarna.get_all_rule_names()

    results = analyze_file(test_file, all_rules)

    # filter results to test the # amarna: disable= rule
    results = filter_results_from_disable(results)

    # Generate summary and compare with the expected result
    summary = create_summary(results)
    compare_expected(summary, FILE)

    load_sarif(results)


def _test_directory(filename: str) -> None:
    if not os.path.isdir(filename):
        return

    test_name = os.path.basename(filename)

    all_rules = Amarna.get_all_rule_names()

    results = analyze_directory(filename, all_rules)

    # Generate summary and compare with the expected result
    summary = create_summary(results)
    compare_expected(summary, test_name)

    load_sarif(results)
