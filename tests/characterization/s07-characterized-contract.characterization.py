import json

print(
    json.dumps(
        {
            "behavior": {"contract": "PASS"},
            "scenario": "s07-characterized-contract",
            "schema_version": "1.0",
        },
        sort_keys=True,
    )
)
