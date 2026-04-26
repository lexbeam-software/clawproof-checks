#!/usr/bin/env python3
"""Regenerate skills/clawproof-audit/checks.json from checks/*.yaml.

Run whenever a YAML check is added, removed, or modified.
"""
import yaml
import json
import glob
import sys


def build() -> int:
    checks = []
    for path in sorted(glob.glob("checks/*.yaml")):
        with open(path) as f:
            checks.append(yaml.safe_load(f))

    out = {
        "version": "1.0.0",
        "source": "https://github.com/lexbeam-software/clawproof-checks",
        "license": "MIT",
        "count": len(checks),
        "checks": checks,
    }

    with open("skills/clawproof-audit/checks.json", "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Generated checks.json with {len(checks)} checks")
    return 0


if __name__ == "__main__":
    sys.exit(build())
