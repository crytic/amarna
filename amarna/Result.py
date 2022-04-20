from typing import Any, Optional, Dict, Union, Tuple
from typing import List
import os
from lark import Tree, Token
import json


# line, column, end_line, end_column
# TODO (montyly): consider creating a namedtuple
PositionType = Tuple[int, int, int, int]


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
        return f"[{self.rule_name}] in {short_name}:{self.position[0]}:{self.position[1]}"

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
        filename: str,
        related_filename: str,
        rule_name: str,
        text: str,
        position_list: List[PositionType],
    ) -> None:
        self.filename = filename
        self.related_filename = related_filename
        self.rule_name = rule_name
        self.text = text
        self.position_list = position_list

    def to_sarif(self) -> Dict:
        return {
            "ruleId": self.rule_name,
            "level": "warning",
            "message": {"text": self.text},
            "locations": [
                {
                    "physicalLocation": {
                        "artifactLocation": {"uri": "file://" + self.filename, "index": 0},
                        "region": sarif_region_from_position(self.position_list[0]),
                    },
                }
            ],
            "relatedLocations": [
                {
                    "id": 0,
                    "physicalLocation": {
                        "artifactLocation": {"uri": "file://" + self.filename, "index": 0},
                        "region": sarif_region_from_position(self.position_list[0]),
                    },
                },
                {
                    "id": 1,
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": "file://" + self.related_filename,
                            "index": 0,
                        },
                        "region": sarif_region_from_position(self.position_list[1]),
                    },
                },
            ],
        }

    def to_summary(self) -> str:
        short_name = os.path.basename(self.filename)
        related_short_name = os.path.basename(self.related_filename)
        return f"[{self.rule_name}] {self.text} in {short_name}:{self.position_list[0][0]}:{self.position_list[0][1]} and {related_short_name}:{self.position_list[1][0]}:{self.position_list[1][1]}"


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
    filename: str,
    related_filename: str,
    rule_name: str,
    text: str,
    position_list: List[PositionType],
) -> ResultMultiplePositions:
    return ResultMultiplePositions(filename, related_filename, rule_name, text, position_list)


def create_sarif(
    results: List[Any], fname: Optional[str] = None, printoutput: bool = False
) -> None:
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

    if printoutput:
        print(json.dumps(sarif))


def sarif_region_from_position(position: PositionType) -> Dict[str, int]:
    """
    Return the sarif region field for a code location
    """
    start_line, start_col, end_line, end_col = position
    return {
        "startLine": start_line,
        "startColumn": start_col,
        "endLine": end_line,
        "endColumn": end_col,
    }


SarifOuputType = Dict[str, Any]


def token_positions(token: Token) -> PositionType:
    """
    Get the file locations of a token: line, col, end_line, end_col
    """
    return (
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
    return (meta.line, meta.column, meta.end_line, meta.end_column)
