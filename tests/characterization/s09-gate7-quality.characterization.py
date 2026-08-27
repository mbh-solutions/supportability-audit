import ast
import json
import os
from pathlib import Path

target = Path(os.environ["SUPPORTABILITY_CHARACTERIZATION_TARGET"])
definition = Path(os.environ["SUPPORTABILITY_CHARACTERIZATION_DEFINITION"])
relative_module = Path("src/supportability_audit/s09_gate7_canary.py")
definition_module = definition / relative_module


def definition_canary(path: Path) -> object:
    for statement in ast.parse(path.read_text(encoding="utf-8")).body:
        if isinstance(statement, ast.Assign):
            for assignment_target in statement.targets:
                if (
                    isinstance(assignment_target, ast.Name)
                    and assignment_target.id == "S09_GATE7_CANARY"
                ):
                    return ast.literal_eval(statement.value)
        if (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == "S09_GATE7_CANARY"
            and statement.value is not None
        ):
            return ast.literal_eval(statement.value)
    raise RuntimeError("S09 Gate 7 canary assignment is missing from the head definition")


if (target / relative_module).is_file():
    from supportability_audit.s09_gate7_canary import S09_GATE7_CANARY
elif definition_module.is_file():
    S09_GATE7_CANARY = definition_canary(definition_module)
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
