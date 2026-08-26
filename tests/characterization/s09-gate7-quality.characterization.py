import json

print(
    json.dumps(
        {
            "behavior": {"quality_canary": "s09-gate7-quality"},
            "scenario": "s09-gate7-quality",
            "schema_version": "1.0",
        },
        sort_keys=True,
    )
)
