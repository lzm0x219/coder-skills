"""Controlled behavior witnesses. This does not measure agent review quality."""
import argparse
import json
from pathlib import Path
import queue
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo

CORPUS = json.loads((Path(__file__).resolve().parents[1] / "cases/comprehensive-corpus.json").read_text())
CASES = {item["id"]: item for item in CORPUS["cases"]}


def namespace(case, side):
    result = {}
    exec(compile(CASES[case][side], CASES[case]["file"], "exec"), result)
    return result


class ExtendedWitnesses(unittest.TestCase):
    def test_q2_ack_after_durable_failure(self):
        # Real SQLite rollback, modeled broker redelivery policy.
        for side, expected_ack in (("baseline", []), ("target", ["m1"])):
            with sqlite3.connect(":memory:") as db:
                db.execute("CREATE TABLE messages (id TEXT PRIMARY KEY)")
                acked = []

                class Storage:
                    def insert(self, message):
                        with db:
                            db.execute("INSERT INTO messages VALUES (?)", (message,))
                            raise OSError("storage failed before commit")

                class Broker:
                    def ack(self, message):
                        acked.append(message)

                with self.assertRaises(OSError):
                    namespace("case-01", side)["consume"]("m1", Storage(), Broker())
                self.assertEqual(db.execute("SELECT * FROM messages").fetchall(), [])
                self.assertEqual(acked, expected_ack)
                self.assertEqual("m1" not in acked, side == "baseline")

    def test_k1_cli_real_process_output(self):
        for side in ("baseline", "target"):
            with tempfile.TemporaryDirectory(prefix="review-cli-") as temp:
                file = Path(temp) / "cli.py"
                file.write_text(CASES["case-02"][side])
                proc = subprocess.run([sys.executable, "-B", str(file), "--json"],
                                      capture_output=True, text=True, check=False)
                self.assertEqual(proc.returncode, 0)
                if side == "baseline":
                    self.assertEqual(json.loads(proc.stdout), {"ok": True})
                else:
                    with self.assertRaises(json.JSONDecodeError):
                        json.loads(proc.stdout)

    def test_w2_missing_middleware_does_not_prove_auth_bypass(self):
        class User:
            name = "Ada"

        class Request:
            user = User()

        self.assertEqual(namespace("case-03", "target")["handle"](Request())["name"], "Ada")
        # The corpus explicitly lacks router/session evidence; handler success
        # proves only the injected object's behavior, not anonymous reachability.
        self.assertIn("无法取得 middleware", CASES["case-03"]["contract"])

    def test_h2_missing_target_timing_is_preserved(self):
        self.assertIn("无编译器目标", CASES["case-04"]["contract"])
        self.assertNotIn("clock", CASES["case-04"]["target"])
        # This is a fixture-precondition check, not a hardware timing witness.

    def test_e3_fit_separation(self):
        self.assertEqual(namespace("case-05", "baseline")["transform"]([0, 2], [100]), [99])
        self.assertEqual(namespace("case-05", "target")["transform"]([0, 2], [100]), [66])

    def test_p1_reconstruction_in_persistence_model(self):
        for side, expected in (("baseline", "saved"), ("target", "")):
            durable = {}
            draft = namespace("case-06", side)["Draft"]
            draft(durable).save("saved")
            self.assertEqual(durable["text"], "saved")
            self.assertEqual(draft(durable).text, expected)

    def test_n1_documented_command_real_process(self):
        source = "import argparse\np=argparse.ArgumentParser()\np.add_argument('--json',action='store_true')\np.parse_args()\n"
        with tempfile.TemporaryDirectory(prefix="review-doc-") as temp:
            file = Path(temp) / "cli.py"
            file.write_text(source)
            for flag, expected in (("--json", 0), ("--machine", 2)):
                proc = subprocess.run([sys.executable, "-B", str(file), flag],
                                      capture_output=True, check=False)
                self.assertEqual(proc.returncode, expected)

    def test_r1_hard_bound_counterevidence(self):
        for length in (0, 1, 8, 9, 10000):
            data = list(range(length))
            old = namespace("case-08", "baseline")["pairs"](data)
            new = namespace("case-08", "target")["pairs"](data)
            self.assertEqual(old, new)
            self.assertLessEqual(len(new), 64)

    def test_q1_actual_bounded_queue(self):
        bounded = queue.Queue(maxsize=2)
        bounded.put_nowait(1)
        bounded.put_nowait(2)
        with self.assertRaises(queue.Full):
            bounded.put_nowait(3)
        self.assertEqual(bounded.get_nowait(), 1)
        bounded.put_nowait(3)
        self.assertEqual(bounded.qsize(), 2)

    def test_v1_rounding_position_changes_total(self):
        values = [Decimal("0.005"), Decimal("0.005")]
        per_item = sum(v.quantize(Decimal("0.01")) for v in values)
        per_total = sum(values).quantize(Decimal("0.01"))
        self.assertEqual((per_item, per_total), (Decimal("0.00"), Decimal("0.01")))
        # The witness proves a difference; the business must select a policy.

    def test_v2_repeated_local_hour_is_two_instants(self):
        zone = ZoneInfo("America/New_York")
        a = datetime(2024, 11, 3, 1, 30, tzinfo=zone, fold=0)
        b = datetime(2024, 11, 3, 1, 30, tzinfo=zone, fold=1)
        self.assertEqual((b.astimezone(timezone.utc) - a.astimezone(timezone.utc)).total_seconds(), 3600)

    def test_v3_byte_prefix_is_not_text_prefix(self):
        value = "中文"
        self.assertEqual(value[:1], "中")
        with self.assertRaises(UnicodeDecodeError):
            value.encode("utf-8")[:1].decode("utf-8")


if __name__ == "__main__":
    unittest.main()
