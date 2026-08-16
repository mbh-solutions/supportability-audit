from __future__ import annotations

import json

from supportability_audit import validate_repository

errors: list[str] = []
validate_repository.validate_standard(errors)
validate_repository.validate_links(errors)
validate_repository.validate_runtime_boundary(errors)
print(
    json.dumps(
        {
            "schema_version": "1.0",
            "scenario": "repository-contract-validation-v2",
            "behavior": {"errors": errors},
        },
        sort_keys=True,
    )
)
