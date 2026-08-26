import json
import os
from pathlib import Path

target = Path(os.environ["SUPPORTABILITY_CHARACTERIZATION_TARGET"])
definition = Path(os.environ["SUPPORTABILITY_CHARACTERIZATION_DEFINITION"])
relative_module = Path("src/supportability_audit/s09_gate7_canary.py")
if (target / relative_module).is_file():
    from supportability_audit.s09_gate7_canary import S09_GATE7_CANARY
elif (definition / relative_module).is_file():
    S09_GATE7_CANARY = "s09-gate7-quality"
else:
    raise RuntimeError("S09 Gate 7 canary module is missing from the head definition")

print(
    json.dumps(
        {
            "behavior": {"quality_canary": S09_GATE7_CANARY},
            "scenario": "s09-gate7-quality",
            "schema_version": "1.0",
        },
        sort_keys=True,
    )
)
