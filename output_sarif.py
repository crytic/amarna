import os
from typing import Any, List, Optional
import json


def create_sarif(
    results: List[Any], fname: Optional[str] = None, printoutput: bool = False
) -> None:
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
