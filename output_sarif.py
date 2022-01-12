from typing import Any, List, Optional, Dict
import json
import os

from lark.lexer import Token


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
        with open(os.path.join(os.getcwd(), fname), "w") as f:
            json.dump(sarif, f, indent=1)

    if printoutput:
        print(json.dumps(sarif))


def generic_sarif(filename: str, rule_name, text, positions) -> Dict[str, Any]:
    """
    Return a SARIF dictionary for a filename, rule, text description and code location.
    """
    start_line, start_col, end_line, end_col = positions
    return {
        "ruleId": rule_name,
        "level": "warning",
        "message": {"text": text},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": "file://" + filename, "index": 0},
                    "region": {
                        "startLine": start_line,
                        "startColumn": start_col,
                        "endLine": end_line,
                        "endColumn": end_col,
                    },
                }
            }
        ],
    }


def token_positions(token: Token):
    return (
        token.line,
        token.column,
        token.end_line,
        token.end_column,
    )


def generic_sarif_token(
    filename: str, rule_name: str, text: str, token: Token
) -> Dict[str, Any]:
    """
    Return a SARIF dictionary for a token.
    """
    return generic_sarif(filename, rule_name, text, token_positions(token))
