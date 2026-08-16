from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


target = Path(os.environ["SUPPORTABILITY_CHARACTERIZATION_TARGET"])
completed = subprocess.run(
    [sys.executable, "-P", "src/supportability_audit/validate_repository.py"],
    cwd=target,
    capture_output=True,
    text=True,
    check=False,
)
print(
    json.dumps(
        {
            "schema_version": "1.0",
            "scenario": "repository-contract-validation",
            "behavior": {
                "exit_code": completed.returncode,
                "stdout": completed.stdout,
            },
        },
        sort_keys=True,
    )
)
