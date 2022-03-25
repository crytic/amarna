from typing import Any, List, Optional, Dict, Tuple
import json
import os

from lark.lexer import Token
from lark import Tree


def create_sarif(
    results: List[Any], fname: Optional[str] = None, printoutput: bool = False
) -> None:
    """
    Create the sarif output json for the results, and write it to file or print it.
    """
    sarif = {
        "version": "2.1.0",
        "$schema": "http://json.schemastore.org/sarif-2.1.0-rtm.4",
        "runs": [{"tool": {"driver": {"name": "Amarna"}}, "results": results}],
    }

    if fname:
        with open(os.path.join(os.getcwd(), fname), "w", encoding="utf8") as f:
            json.dump(sarif, f, indent=1)

    if printoutput:
        print(json.dumps(sarif))


def sarif_region_from_position(position):
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


def generic_sarif(filename: str, rule_name, text, position) -> Dict[str, Any]:
    """
    Return a SARIF dictionary for a filename, rule, text description and code location.
    """
    return {
        "ruleId": rule_name,
        "level": "warning",
        "message": {"text": text},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": sarif_region_from_position(position),
                }
            }
        ],
    }


def generic_sarif_two_positions(
    filename: str, relatedfilename: str, rule_name, text, position_list
):
    return {
        "ruleId": rule_name,
        "level": "warning",
        "message": {"text": text},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": sarif_region_from_position(position_list[0]),
                },
            }
        ],
        "relatedLocations": [
            {
                "id": 0,
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": sarif_region_from_position(position_list[0]),
                },
            },
            {
                "id": 1,
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": "file://" + relatedfilename,
                        "index": 0,
                    },
                    "region": sarif_region_from_position(position_list[1]),
                },
            },
        ],
    }


def token_positions(token: Token):
    """
    Get the file locations of a token: line, col, end_line, end_col
    """
    return (
        token.line,
        token.column,
        token.end_line,
        token.end_column,
    )


def getPosition(tree: Tree) -> Tuple[int, int, int, int]:
    """
    Get the file locations of the tree: line, col, end_line, end_col
    """
    meta = tree.meta
    return (meta.line, meta.column, meta.end_line, meta.end_column)


def generic_sarif_token(filename: str, rule_name: str, text: str, token: Token) -> Dict[str, Any]:
    """
    Return a SARIF dictionary for a token.
    """
    return generic_sarif(filename, rule_name, text, token_positions(token))
