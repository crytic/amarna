import os
from pathlib import Path

from amarna.amarna import analyze_directory, analyze_file
from amarna.Result import create_summary

_module_dir = Path(__file__).resolve().parent
TESTS_DIR = _module_dir


def test_all():
    for subdir, _dirs, files in os.walk(TESTS_DIR):
        for file in files:
            _test_single(file)


def _test_single(filename):
    FILE, ext = os.path.splitext(filename)
    if ext != '.cairo':
        return

    test_file = str(TESTS_DIR.joinpath(FILE + ext))
    results = analyze_file(test_file)
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
            expected = f.write(summary)

