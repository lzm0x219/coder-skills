"""验证案例的真实行为与 Git 范围语义，不替代智能体审查评测。"""

import hashlib
import importlib.util
import json
import pathlib
import subprocess
import tempfile
import unittest


FIXTURES = pathlib.Path(__file__).resolve().parents[1] / "cases"


def load(name):
    spec = importlib.util.spec_from_file_location(name, FIXTURES / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class BehaviorWitnesses(unittest.TestCase):
    def test_legal_zero_regresses_but_missing_remains_valid(self):
        before, after = load("baseline"), load("target")
        self.assertEqual(before.effective_limit(0), 0)
        self.assertEqual(after.effective_limit(0), 20)
        self.assertEqual(before.effective_limit(None), after.effective_limit(None))
        self.assertEqual(before.effective_limit(5), after.effective_limit(5))

    def test_cross_tenant_access_becomes_reachable(self):
        before, after = load("baseline"), load("target")
        orders = {"42": {"tenant": "A", "amount": 100}}
        self.assertIsNone(before.read_order(orders, "42", "B"))
        self.assertEqual(after.read_order(orders, "42", "B"), orders["42"])
        self.assertEqual(before.read_order(orders, "42", "A"), orders["42"])

    def test_guard_disproves_zero_regression(self):
        guarded = load("guarded")
        items = list(range(30))
        for limit in (None, -1, 0, 1, 20, 50):
            expected = [] if limit is not None and limit <= 0 else items[:20 if limit is None else limit]
            self.assertEqual(guarded.list_items(items, limit), expected)

    def test_old_problem_is_unchanged(self):
        before, after = load("baseline"), load("target")
        self.assertEqual(before.legacy_discount(-5), 5)
        self.assertEqual(after.legacy_discount(-5), 5)


class IndependentWitnessReplay(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = {case["id"]: case for case in json.loads((FIXTURES / "independent-cases.json").read_text())}

    def version(self, case_id, version):
        namespace = {}
        # 仓库中保留的受控可信夹具；不接收外部代码作为输入。
        exec(compile(self.cases[case_id][version], f"{case_id}/{version}.py", "exec"), namespace)
        return namespace

    def test_boundary_rewrite_preserves_declared_inputs(self):
        case_id = "01-legal-boundary"
        before, after = self.version(case_id, "before"), self.version(case_id, "target")
        for limit in (None, 0, 1, 20, 100):
            self.assertEqual(before["limit_rows"]([1, 2, 3], limit), after["limit_rows"]([1, 2, 3], limit))
        for version in (before, after):
            for limit in (-1, 101):
                with self.assertRaises(ValueError):
                    version["limit_rows"]([1, 2, 3], limit)

    def test_tenant_predicate_removal_leaks_other_tenant(self):
        case_id = "02-cross-tenant"
        records = [{"tenant_id": "A"}, {"tenant_id": "B"}]
        self.assertEqual(self.version(case_id, "before")["read_records"](records, "A"), records[:1])
        self.assertEqual(self.version(case_id, "target")["read_records"](records, "A"), records)

    def test_guard_case_is_equivalent_only_for_verified_conditions(self):
        case_id = "03-equivalent-guard"
        records = [{"tenant_id": "A"}, {"tenant_id": "B"}]
        before, after = self.version(case_id, "before"), self.version(case_id, "target")
        self.assertEqual(before["read_records"](records, "A"), after["read_records"](records, "A"))
        for version in (before, after):
            with self.assertRaises(ValueError):
                version["read_records"](records, None)
        # 空字符串语义未被契约明定，必须保留这项真实行为变化。
        with self.assertRaises(ValueError):
            before["read_records"](records, "")
        self.assertEqual(after["read_records"](records, ""), [])

    def test_staged_version_is_safe_but_worktree_leaks(self):
        case_id = "04-layered-scope"
        records = [{"tenant_id": "A"}, {"tenant_id": "B"}]
        self.assertEqual(self.version(case_id, "index")["read_records"](records, "A"), records[:1])
        self.assertEqual(self.version(case_id, "target")["read_records"](records, "A"), records)


class GitScopeWitnesses(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="coder-review-cases-")
        self.addCleanup(self.tmp.cleanup)
        self.root = pathlib.Path(self.tmp.name)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Review Fixture")
        self.git("config", "user.email", "review@example.invalid")
        self.write("module.py", "value = 1\n")
        self.git("add", "--", "module.py")
        self.git("commit", "-qm", "baseline")
        self.base = self.git("rev-parse", "HEAD").decode().strip()

    def git(self, *args, check=True):
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=check,
            env=self.clean_env(),
        )
        return result.stdout if check else result

    @staticmethod
    def clean_env():
        import os
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"})
        return env

    def write(self, path, text):
        (self.root / path).write_text(text, encoding="utf-8")

    def test_index_worktree_and_untracked_are_distinct(self):
        self.write("module.py", "value = 2\n")
        self.git("add", "--", "module.py")
        self.write("module.py", "value = 3\n")
        strange = "new file\nwith newline.py"
        self.write(strange, "value = 4\n")
        self.assertEqual(self.git("show", ":module.py"), b"value = 2\n")
        self.assertEqual((self.root / "module.py").read_bytes(), b"value = 3\n")
        self.assertIn(b"+value = 2", self.git("diff", "--cached", self.base, "--"))
        self.assertIn(b"+value = 3", self.git("diff", "--"))
        files = self.git("ls-files", "--others", "--exclude-standard", "-z").split(b"\0")
        self.assertIn(strange.encode(), files)
        before = hashlib.sha256((self.root / strange).read_bytes()).hexdigest()
        self.write(strange, "value = 5\n")
        after = hashlib.sha256((self.root / strange).read_bytes()).hexdigest()
        self.assertNotEqual(before, after)

    def test_endpoints_and_branch_contribution_differ(self):
        self.git("switch", "-qc", "topic")
        self.write("module.py", "value = 2\n")
        self.git("commit", "-qam", "topic change")
        target = self.git("rev-parse", "HEAD").decode().strip()
        self.git("switch", "-q", "main")
        self.write("base-only.py", "base_only = True\n")
        self.git("add", "--", "base-only.py")
        self.git("commit", "-qm", "base advance")
        advanced = self.git("rev-parse", "HEAD").decode().strip()
        merge_base = self.git("merge-base", advanced, target).decode().strip()
        exact = self.git("diff", "--name-only", "-z", advanced, target, "--")
        contribution = self.git("diff", "--name-only", "-z", merge_base, target, "--")
        self.assertIn(b"base-only.py\0", exact)
        self.assertNotIn(b"base-only.py\0", contribution)
        self.assertIn(b"module.py\0", contribution)

    def test_invalid_ref_and_empty_diff_are_different_states(self):
        result = self.git("rev-parse", "--verify", "missing-ref^{commit}", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.git("diff", self.base, self.base, "--"), b"")

    def test_conflict_is_visible_and_not_an_empty_diff(self):
        self.git("switch", "-qc", "topic")
        self.write("module.py", "value = 2\n")
        self.git("commit", "-qam", "topic")
        self.git("switch", "-q", "main")
        self.write("module.py", "value = 3\n")
        self.git("commit", "-qam", "main")
        result = self.git("merge", "topic", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"UU module.py\0", self.git("status", "--porcelain=v1", "-z"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
