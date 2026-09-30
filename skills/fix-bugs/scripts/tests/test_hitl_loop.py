"""The manual reproduction loop exposes an unambiguous check result."""

from pathlib import Path
import subprocess
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "hitl-loop.sh"


class HitlLoopTests(unittest.TestCase):
    def test_observation_controls_verdict_and_exit_status(self) -> None:
        for answer, verdict, status in [("y", "RED", 1), ("n", "GREEN", 0), ("u", "UNKNOWN", 3)]:
            with self.subTest(answer=answer):
                result = subprocess.run(
                    ["bash", str(SCRIPT), "Export throws", "Click Export"],
                    input=f"\n{answer}\nredacted note\n",
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(result.returncode, status, result.stderr)
                self.assertIn(f"REPRO_VERDICT={verdict}", result.stdout)
                self.assertIn("REPRO_NOTE=redacted note", result.stdout)

    def test_missing_observation_is_not_a_green_result(self) -> None:
        result = subprocess.run(
            ["bash", str(SCRIPT), "Export throws", "Click Export"],
            input="\n",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("REPRO_VERDICT=GREEN", result.stdout)


if __name__ == "__main__":
    unittest.main()
