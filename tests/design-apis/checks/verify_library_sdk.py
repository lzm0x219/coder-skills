#!/usr/bin/env python3
"""Recheck design-time library/SDK contract fixtures without running a service."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


TEST_ROOT = Path(__file__).resolve().parents[1]
ROOT = TEST_ROOT.parents[1]
SKILL_ROOT = ROOT / "skills/design-apis"
FIXTURES = TEST_ROOT / "cases"


def run(label: str, command: list[str], cwd: Path, *, failure: tuple[str, ...] | None = None) -> None:
    result = subprocess.run(
        ["rtk", "proxy", *command],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    diagnostics = result.stdout + result.stderr
    if failure is None:
        passed = result.returncode == 0
    else:
        error_lines = [line for line in diagnostics.splitlines() if "error TS" in line]
        passed = result.returncode != 0 and len(error_lines) == 1 and all(
            expected in error_lines[0] for expected in failure
        )
    if not passed:
        print(f"FAIL {label}: exit {result.returncode}\n{diagnostics}", file=sys.stderr)
        raise SystemExit(1)
    print(f"PASS {label}")


def check_markdown() -> None:
    files = [
        ROOT / "README.md",
        *ROOT.joinpath("docs").rglob("*.md"),
        *SKILL_ROOT.rglob("*.md"),
    ]
    errors: list[str] = []
    for file in files:
        content = file.read_text(encoding="utf-8")
        if sum(line.startswith("```") for line in content.splitlines()) % 2:
            errors.append(f"{file.relative_to(ROOT)}: unclosed code fence")
        for target in re.findall(r"(?<!!)\[[^]]+\]\(([^)]+)\)", content):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0]
            if path and not (file.parent / path).exists():
                errors.append(f"{file.relative_to(ROOT)}: missing {target}")
    if errors:
        raise SystemExit("FAIL Markdown links/fences:\n" + "\n".join(errors))
    print(f"PASS Markdown links/fences ({len(files)} files)")


def main() -> None:
    check_markdown()
    with tempfile.TemporaryDirectory(prefix="coder-library-sdk-") as workspace:
        temporary = Path(workspace)
        temporary.joinpath("package.json").write_text(
            json.dumps(
                {
                    "private": True,
                    "dependencies": {
                        "typescript": "5.6.3",
                        "@aws-sdk/client-s3": "3.1142.0",
                        "@types/node": "24.19.0",
                    },
                }
            ),
            encoding="utf-8",
        )
        run("temporary TypeScript dependencies", ["pnpm", "install", "--ignore-scripts"], temporary)
        tsc = str(temporary / "node_modules" / ".bin" / "tsc")

        evolution = FIXTURES / "typescript-sdk-evolution"
        for version in ("v1", "candidate"):
            run(f"TypeScript {version} consumer", [tsc, "-p", f"tsconfig.{version}.json"], evolution)
        run(
            "TypeScript broken contract rejected",
            [tsc, "-p", "tsconfig.broken.json"],
            evolution,
            failure=("error TS2353", "'limit' does not exist"),
        )

        common = [tsc, "--noEmit", "--strict", "--target", "ES2022", "--module", "NodeNext", "--moduleResolution", "NodeNext"]
        run(
            "FileFlow and webhook fixtures",
            common
            + [
                "fileflow-sdk.api.ts",
                "fileflow-sdk.usage.ts",
                "stripe-webhook-verifier.api.ts",
                "stripe-webhook-verifier.usage.ts",
            ],
            FIXTURES,
        )
        run(
            "S3 multipart fixture",
            common
            + [
                "--baseUrl", str(temporary / "node_modules"),
                "--typeRoots", str(temporary / "node_modules" / "@types"),
                "--types", "node",
                "s3-multipart-sdk.api.ts",
                "s3-multipart-sdk.usage.ts",
            ],
            FIXTURES,
        )

        run(
            "Python audit SDK types",
            ["pnpm", "dlx", "--package", "pyright@1.1.414", "pyright", "-p", "pyrightconfig.json"],
            FIXTURES / "python-audit-sdk",
        )
        run(
            "Rust blob contract",
            ["cargo", "check", "--examples", "--target-dir", str(temporary / "cargo-target")],
            FIXTURES / "rust-blob-contract",
        )
        audit_rust = FIXTURES / "rust-audit-sdk"
        run("Rust audit SDK format", ["cargo", "fmt", "--check"], audit_rust)
        run(
            "Rust audit SDK consumer",
            ["cargo", "check", "--examples", "--target-dir", str(temporary / "cargo-target")],
            audit_rust,
        )
        run(
            "Rust audit SDK strict Clippy",
            ["cargo", "clippy", "--examples", "--target-dir", str(temporary / "cargo-target"), "--", "-D", "warnings"],
            audit_rust,
        )


if __name__ == "__main__":
    main()
