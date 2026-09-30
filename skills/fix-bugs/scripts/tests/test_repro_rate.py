"""Behavioral regression for interrupted flaky-reproduction sampling."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest


RUNNER = Path(__file__).resolve().parents[1] / "repro-rate.py"


class ReproRateTests(unittest.TestCase):
    @unittest.skipUnless(os.name == "posix", "signal behavior is POSIX specific")
    def test_check_can_handle_its_own_sigterm(self) -> None:
        child = (
            "import os,signal,sys; "
            "signal.signal(signal.SIGTERM, lambda *_: sys.exit(42)); "
            "os.kill(os.getpid(), signal.SIGTERM)"
        )
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--runs", "1", "--timeout", "2", "--", sys.executable, "-c", child],
            capture_output=True,
            text=True,
            check=False,
            timeout=4,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        sample = json.loads(result.stdout)
        self.assertEqual(sample["return_codes"], {"42": 1})
        self.assertEqual(sample["timeout"], 0)

    @unittest.skipUnless(os.name == "posix", "process-group behavior is POSIX specific")
    def test_signal_during_spawn_stops_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "survived"
            wrapper = """
import importlib.util
import os
import signal
import subprocess
import sys
import time

spec = importlib.util.spec_from_file_location("repro_rate", sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
original_popen = subprocess.Popen

def interrupted_popen(*args, **kwargs):
    process = original_popen(*args, **kwargs)
    os.kill(os.getpid(), signal.SIGTERM)
    time.sleep(0.05)
    return process

module.subprocess.Popen = interrupted_popen
child = "import pathlib,sys,time; time.sleep(0.35); pathlib.Path(sys.argv[1]).write_text('alive')"
sys.argv = [sys.argv[1], "--runs", "1", "--timeout", "3", "--", sys.executable, "-c", child, sys.argv[2]]
raise SystemExit(module.main())
"""
            result = subprocess.run(
                [sys.executable, "-c", wrapper, str(RUNNER), str(marker)],
                capture_output=True,
                text=True,
                check=False,
                timeout=3,
            )
            time.sleep(0.4)
            self.assertEqual(result.returncode, 143, result.stderr)
            self.assertFalse(marker.exists(), "signal during Popen left the check running")

    def test_nonfinite_timeout_is_rejected_before_running_check(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory) / "check-ran"
            code = "import sys,pathlib; pathlib.Path(sys.argv[1]).write_text('ran')"
            for timeout in ("nan", "inf", "-inf"):
                with self.subTest(timeout=timeout):
                    result = subprocess.run(
                        [sys.executable, str(RUNNER), "--runs", "1", "--timeout", timeout, "--", sys.executable, "-c", code, str(marker)],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    self.assertEqual(result.returncode, 2)
                    self.assertFalse(marker.exists(), "invalid timeout ran the check")

    @unittest.skipUnless(os.name == "posix", "process-group behavior is POSIX specific")
    def test_termination_stops_spawned_child(self) -> None:
        for termination_signal, expected_code in ((signal.SIGINT, 130), (signal.SIGTERM, 143)):
            with self.subTest(termination_signal=termination_signal), tempfile.TemporaryDirectory() as directory:
                ready = Path(directory) / "ready"
                survived = Path(directory) / "survived"
                child_code = "import sys,time,pathlib; time.sleep(0.4); pathlib.Path(sys.argv[1]).write_text('alive')"
                parent_code = (
                    "import subprocess,sys,time,pathlib; "
                    "subprocess.Popen([sys.executable,'-c',sys.argv[1],sys.argv[3]]); "
                    "pathlib.Path(sys.argv[2]).write_text('ready'); time.sleep(3)"
                )
                runner = subprocess.Popen(
                    [sys.executable, str(RUNNER), "--runs", "1", "--timeout", "5", "--", sys.executable, "-c", parent_code, child_code, str(ready), str(survived)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                try:
                    deadline = time.monotonic() + 2
                    while not ready.exists() and time.monotonic() < deadline:
                        time.sleep(0.01)
                    self.assertTrue(ready.exists(), "test check did not start")
                    os.kill(runner.pid, termination_signal)
                    _, error = runner.communicate(timeout=2)
                    time.sleep(0.45)
                    self.assertFalse(survived.exists(), "terminated check left a child running")
                    self.assertEqual(runner.returncode, expected_code, error)
                finally:
                    if runner.poll() is None:
                        runner.kill()
                        runner.wait()


if __name__ == "__main__":
    unittest.main()
