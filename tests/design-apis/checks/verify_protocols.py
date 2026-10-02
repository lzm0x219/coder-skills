#!/usr/bin/env python3
"""Check protocol contracts and representative local execution fixtures."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


HERE = Path(__file__).resolve().parent


def run(label: str, command: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(
        ["rtk", "proxy", *command], cwd=cwd, env=env,
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        print(f"FAIL {label}: exit {result.returncode}\n{result.stdout}{result.stderr}", file=sys.stderr)
        raise SystemExit(1)
    if label == "temporary protocol validators":
        print(f"PASS {label}")
    elif result.stdout.strip():
        print(result.stdout.strip())
    if result.stderr.strip():
        print(result.stderr.strip())


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="coder-design-apis-") as workspace:
        temporary = Path(workspace)
        (temporary / "package.json").write_text(
            json.dumps({
                "private": True,
                "dependencies": {
                    "@apidevtools/swagger-parser": "13.1.0",
                    "graphql": "16.14.2",
                    "ajv": "8.20.0",
                    "ajv-formats": "3.0.1",
                },
            }), encoding="utf-8",
        )
        run("temporary protocol validators", ["pnpm", "install", "--ignore-scripts"], temporary)
        env = os.environ.copy()
        env["NODE_PATH"] = str(temporary / "node_modules")
        for script in ("verify_http_graphql.cjs", "verify_events_webhooks.cjs"):
            run(script, ["node", str(HERE / script), str(HERE.parent / "cases")], temporary, env=env)
    run("RPC generation and local execution", [sys.executable, str(HERE / "verify_rpc.py")], HERE)


if __name__ == "__main__":
    main()
