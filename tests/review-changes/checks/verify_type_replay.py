"""Replay persisted independent sources. Host behavior is not device proof."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ARCHIVE = json.loads((Path(__file__).resolve().parents[1] / "cases/all-types-source.json").read_text())


def run_source(kind, side, name, args=(), compiler=None):
    with tempfile.TemporaryDirectory(prefix="review-type-") as temp:
        directory = Path(temp)
        prefix = f"source-v2/{kind}/{side}/"
        selected = {key: item for key, item in ARCHIVE.items() if key.startswith(prefix)}
        if not selected:
            raise AssertionError("missing archived version: " + prefix)
        for key, item in selected.items():
            file = directory / key.removeprefix(prefix)
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text(item["text"])
        if compiler:
            compiled = directory / "host-test"
            command = [compiler, name, "-o", str(compiled)]
            if compiler == "clang":
                command[1:1] = ["-std=c11", "-Wall", "-Wextra", "-Werror"]
            subprocess.run(command, cwd=directory, capture_output=True, text=True, check=True)
            command = [str(compiled), *args]
        elif name.endswith(".py"):
            command = [sys.executable, "-B", name, *args]
        elif name.endswith(".plist"):
            command = ["plutil", "-lint", name]
        else:
            raise AssertionError("unsupported replay")
        return subprocess.run(command, cwd=directory, capture_output=True, text=True, check=False)


class IndependentTypeReplay(unittest.TestCase):
    def test_archive_identity(self):
        for path, item in ARCHIVE.items():
            self.assertEqual(hashlib.sha256(item["text"].encode()).hexdigest(), item["sha256"], path)
        lines = ARCHIVE["source-v2/SHA256SUMS.tsv"]["text"].splitlines()[1:]
        self.assertEqual(len(lines), 32)
        for line in lines:
            kind, side, path, size, digest = line.split("\t")
            item = ARCHIVE[f"source-v2/{kind}/{side}/{path}"]
            self.assertEqual(len(item["text"].encode()), int(size))
            self.assertEqual(item["sha256"], digest)

    def test_web_query_string_counterevidence(self):
        for side in ("baseline", "target"):
            ns = {}
            source = ARCHIVE[f"source-v2/web/{side}/app.py"]["text"]
            exec(compile(source, "app.py", "exec"), ns)
            response = {}
            body = ns["app"]({"QUERY_STRING": "limit=0", "REQUEST_METHOD": "GET"},
                             lambda status, headers: response.update(status=status, headers=headers))
            self.assertEqual(response["status"], "200 OK")
            self.assertEqual(body, [b"[]"])

    def test_cli_guard_real_process(self):
        for side in ("baseline", "target"):
            zero = run_source("cli", side, "cli.py", ("--size", "0"))
            valid = run_source("cli", side, "cli.py", ("--size", "2"))
            self.assertEqual(zero.returncode, 2)
            self.assertIn("must be positive", zero.stderr)
            self.assertEqual((valid.returncode, valid.stdout.strip()), (0, "2"))

    def test_data_threshold_real_process(self):
        old = run_source("data", "baseline", "pipeline.py", ("sample.csv", "0.8"))
        new = run_source("data", "target", "pipeline.py", ("sample.csv", "0.8"))
        self.assertEqual(old.returncode, 0)
        self.assertEqual(new.returncode, 0)
        self.assertEqual(old.stdout.strip(), "['a', 'b']")
        self.assertEqual(new.stdout.strip(), "['b']")

    def test_document_claim_not_runtime_regression(self):
        for side in ("baseline", "target"):
            ns = {}
            exec(compile(ARCHIVE[f"source-v2/docs/{side}/charge.py"]["text"], "charge.py", "exec"), ns)
            ns["charge"](5, "r-1")
            ns["charge"](5, "r-1")
            self.assertEqual(ns["ledger"], [5, 5])

    @unittest.skipUnless(shutil.which("clang"), "host C compiler unavailable")
    def test_embedded_host_modular_elapsed(self):
        old = run_source("embedded", "baseline", "timer.c", compiler="clang")
        new = run_source("embedded", "target", "timer.c", compiler="clang")
        self.assertEqual((old.returncode, new.returncode), (0, 0))
        self.assertEqual((old.stdout.strip(), new.stdout.strip()), ("6", "0"))

    @unittest.skipUnless(shutil.which("swiftc"), "host Swift compiler unavailable")
    def test_app_host_model_not_os_lifecycle(self):
        old = run_source("app", "baseline", "SessionModel.swift", compiler="swiftc")
        new = run_source("app", "target", "SessionModel.swift", compiler="swiftc")
        self.assertEqual((old.returncode, new.returncode), (0, 0))
        self.assertEqual((old.stdout.strip(), new.stdout.strip()), ("draft=unsaved", "draft="))

    @unittest.skipUnless(shutil.which("plutil"), "macOS plist validator unavailable")
    def test_service_format_not_lifecycle(self):
        for side in ("baseline", "target"):
            result = run_source("service", side, "job.plist")
            self.assertEqual(result.returncode, 0)
            self.assertIn("OK", result.stdout)


if __name__ == "__main__":
    unittest.main()
