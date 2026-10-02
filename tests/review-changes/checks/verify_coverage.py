"""Structural inventory checks only; never evidence of review correctness."""
import json
from pathlib import Path
import re
import unittest

TEST_ROOT = Path(__file__).resolve().parents[1]
ROOT = TEST_ROOT.parents[1] / "skills/review-changes"
MANIFEST = json.loads((TEST_ROOT / "methods/coverage.json").read_text())


class CoverageInventory(unittest.TestCase):
    def test_unique_inventory_and_rule_shape(self):
        actual = {}
        for file in sorted((ROOT / "references").rglob("*.md")):
            text = file.read_text()
            matches = list(re.finditer(r"^## ([A-Z]+[0-9]+) .*", text, re.M))
            for index, match in enumerate(matches):
                rule = match.group(1)
                self.assertNotIn(rule, actual)
                actual[rule] = str(file.relative_to(ROOT))
                end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
                section = text[match.end():end]
                for marker in ("触发：", "必须", "完成："):
                    self.assertIn(marker, section, rule)
        expected = {rule: group["path"] for group in MANIFEST["groups"] for rule in group["rules"]}
        self.assertEqual(actual, expected)
        self.assertEqual(len(expected), sum(len(group["rules"]) for group in MANIFEST["groups"]))

    def test_relative_links_and_rule_id_targets(self):
        for file in [ROOT / "SKILL.md", *sorted((ROOT / "references").rglob("*.md")), TEST_ROOT / "methods/capability.md"]:
            for label, target in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", file.read_text()):
                if "://" in target or target.startswith("/"):
                    continue
                destination = target.split("#", 1)[0]
                path = (file.parent / destination).resolve() if destination else file
                self.assertTrue(path.is_file(), (file, target))
                ids = re.findall(r"\b[A-Z]+[0-9]+\b", label)
                if ids:
                    titles = set(re.findall(r"^## ([A-Z]+[0-9]+) ", path.read_text(), re.M))
                    for rule in ids:
                        self.assertIn(rule, titles, (file, label, target))

    def test_declared_type_families_exist(self):
        self.assertEqual(set(MANIFEST["profiles"]),
                         {"web", "services", "tools", "apps", "data-ai", "embedded", "noncode"})
        for profile in MANIFEST["profiles"]:
            self.assertTrue((ROOT / "references/profiles" / (profile + ".md")).is_file())
        entry = (ROOT / "SKILL.md").read_text()
        self.assertIn("references/routing.md", entry)
        routing = (ROOT / "references/routing.md").read_text()
        for profile in MANIFEST["profiles"]:
            self.assertIn("profiles/" + profile + ".md", routing)


if __name__ == "__main__":
    unittest.main()
