from dataclasses import dataclass
from typing import Any, Optional, Dict, Union
from typing import List
import os
from lark import Tree, Token
import json


@dataclass
class PositionType:
    """Tracks the position in a file"""

    start_line: int
    start_col: int
    end_line: int
    end_col: int


class Result:
    def __init__(self, filename: str, rule_name: str, text: str, position: PositionType) -> None:
        self.filename = filename
        self.rule_name = rule_name
        self.text = text
        self.position = position

    def to_sarif(self) -> Dict:
        """
        Return a SARIF dictionary for a filename, rule, text description and code location.
        """
        return {
            "ruleId": self.rule_name,
            "level": "warning",
            "message": {"text": self.text},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": "file://" + self.filename, "index": 0},
                        "region": sarif_region_from_position(self.position),
                    }
                }
            ],
        }

    def to_summary(self) -> str:
        short_name = os.path.basename(self.filename)
        return f"[{self.rule_name}] in {short_name}:{self.position.start_line}:{self.position.start_col}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Result):
            return (
                self.filename == other.filename
                and self.position == other.position
                and self.rule_name == other.rule_name
            )
        return False


class ResultMultiplePositions:
    def __init__(
        self,
        filenames: str,
        rule_name: str,
        text: str,
        position_list: List[PositionType],
    ) -> None:
        assert len(filenames) == len(position_list)
        self.filenames = filenames
        self.rule_name = rule_name
        self.text = text
        self.position_list = position_list

    def to_sarif(self) -> Dict:
        related_location_list = [
            {
                "id": idx,
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": sarif_region_from_position(self.position_list[idx]),
                },
            }
            for idx, filename in enumerate(self.filenames)
        ]
        return {
            "ruleId": self.rule_name,
            "level": "warning",
            "message": {"text": self.text},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": "file://" + self.filenames[0], "index": 0},
                        "region": sarif_region_from_position(self.position_list[0]),
                    },
                }
            ],
            "relatedLocations": related_location_list,
        }

    def to_summary(self) -> str:
        interpolated = [
            f"{os.path.basename(loc)}:{res.start_line}:{res.start_col}"
            for loc, res in zip(self.filenames, self.position_list)
        ]
        if len(interpolated) > 1:
            prefix = " and "
        else:
            prefix = ""

        full_str = ", ".join(interpolated[:-1]) + f"{prefix}{interpolated[-1]}"

        return f"[{self.rule_name}] {self.text} in " + full_str


ResultTypes = Union[Result, ResultMultiplePositions]

SARIF_MODE = "sarif_mode"
SUMMARY_MODE = "summary_mode"


def output_result(results: List[ResultTypes], fname: str, print_output: bool, mode: str) -> None:
    if mode == SARIF_MODE:
        create_sarif(results, fname, print_output)

    elif mode == SUMMARY_MODE:
        summary = create_summary(results)
        if print_output:
            print(summary)

        if fname:
            with open(os.path.join(os.getcwd(), fname), "w", encoding="utf8") as f:
                f.write(summary)


def create_summary(results: List[ResultTypes]) -> str:
    return "\n".join(map(lambda res: res.to_summary(), results))


def create_result(filename: str, rule_name: str, text: str, position: PositionType) -> Result:
    return Result(filename, rule_name, text, position)


def create_result_token(filename: str, rule_name: str, text: str, token: Token) -> Result:
    return Result(filename, rule_name, text, token_positions(token))


def result_multiple_positions(
    filenames: str,
    rule_name: str,
    text: str,
    position_list: List[PositionType],
) -> ResultMultiplePositions:
    return ResultMultiplePositions(filenames, rule_name, text, position_list)


def create_sarif(results: List[Any], fname: Optional[str] = None, printoutput: bool = False) -> str:
    """
    Create the sarif output json for the results, and write it to file or print it.
    """
    results_sarif = list(map(lambda res: res.to_sarif(), results))
    sarif = {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
        "runs": [{"tool": {"driver": {"name": "Amarna"}}, "results": results_sarif}],
    }

    if fname:
        with open(os.path.join(os.getcwd(), fname), "w", encoding="utf8") as f:
            json.dump(sarif, f, indent=1)

    sarif_str = json.dumps(sarif)
    if printoutput:
        print(sarif_str)

    return sarif_str


def sarif_region_from_position(position: PositionType) -> Dict[str, int]:
    """
    Return the sarif region field for a code location
    """
    return {
        "startLine": position.start_line,
        "startColumn": position.start_col,
        "endLine": position.end_line,
        "endColumn": position.end_col,
    }


SarifOuputType = Dict[str, Any]


def token_positions(token: Token) -> PositionType:
    """
    Get the file locations of a token: line, col, end_line, end_col
    """
    return PositionType(
        token.line,
        token.column,
        token.end_line,
        token.end_column,
    )


def getPosition(tree: Tree) -> PositionType:
    """
    Get the file locations of the tree: line, col, end_line, end_col
    """
    meta = tree.meta
    return PositionType(meta.line, meta.column, meta.end_line, meta.end_column)
