"""Validate rule-review evidence; never grade protocol semantics."""

import argparse
import hashlib
import json
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[3] / "skills/design-apis"
DIMENSIONS = {"coverage", "accuracy", "execution", "traceability"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def location(ref):
    path = (SKILL_ROOT / ref["path"]).resolve()
    require(path.is_relative_to(SKILL_ROOT), "rule path escapes Skill")
    data = path.read_bytes()
    require(hashlib.sha256(data).hexdigest() == ref["sha256"], "stale rule SHA")
    lines = data.decode("utf-8").splitlines()
    start, end = ref["lineStart"], ref["lineEnd"]
    require(
        type(start) is int and type(end) is int and 1 <= start <= end <= len(lines),
        "invalid rule line range",
    )
    require("\n".join(lines[start - 1:end]) == ref["quote"], "stale rule quote")


def validate(report):
    require(report["schemaVersion"] == 1, "unsupported schemaVersion")
    require(report["reviewScope"] == "rules", "runtime/capability review is out of scope")
    require(set(report["criteria"]) == DIMENSIONS, "four rule dimensions required")
    require("score" not in report and "overall10" not in report, "numeric overall grade is out of scope")
    scope = report["scope"]
    require(scope["mode"] == "targeted", "this report format declares targeted review")
    require(scope["fullCorpusReviewed"] is False, "targeted review cannot claim full-corpus pass")
    require(bool(scope["notReviewed"]), "unreviewed scope must be stated")
    units = report["units"]
    require(bool(units), "review units required")
    require(len({u["id"] for u in units}) == len(units), "duplicate unit IDs")
    require(set(scope["selectedUnitIds"]) == {u["id"] for u in units}, "scope/unit mismatch")
    for unit in units:
        require(bool(unit["dimensions"]) and set(unit["dimensions"]) <= DIMENSIONS, "invalid dimensions")
        require(bool(unit["rules"]), "current rule locations required")
        for ref in unit["rules"]:
            location(ref)
        require(bool(unit["observations"]), "verified observations required")
        require(bool(unit["basis"]), "source basis required")
        for basis in unit["basis"]:
            for field in ("url", "version", "section", "retrievedAt", "summary"):
                require(bool(basis.get(field)), f"basis.{field} required")
        findings = unit["findings"]
        for finding in findings:
            require(finding["dimension"] in unit["dimensions"], "finding dimension mismatch")
            location(finding["rule"])
            require(finding["rule"] in unit["rules"], "finding must target this unit's rule")
            for field in ("id", "problem", "impact", "fix", "evidence"):
                require(bool(finding.get(field)), f"finding.{field} required")
            for field in ("url", "version", "section"):
                require(bool(finding["authority"].get(field)), f"finding authority.{field} required")
            require(
                any(all(finding["authority"][k] == basis[k] for k in ("url", "version", "section")) for basis in unit["basis"]),
                "finding authority must match the unit's inspected source basis",
            )
        status = unit["status"]
        require(status in {"pass", "needs_fix", "uncertain"}, "invalid status")
        verdict = unit["jev"]
        require(type(verdict["confidence"]) in (int, float), "numeric confidence required")
        require(0 <= verdict["confidence"] <= 1, "confidence out of range")
        reliable = verdict["confidence"] >= 0.7 and verdict["escalate"] is False
        resolution = unit.get("resolution")
        investigated = False
        if resolution:
            require(resolution["author"] == "codex", "resolution author must be explicit")
            require(resolution["status"] == status, "resolution/status mismatch")
            require(bool(resolution["investigation"]) and bool(resolution["evidence"]), "resolution requires investigation and new/independent evidence")
            require(bool(resolution["checkedAt"]), "resolution date required")
            investigated = True
        if status == "pass":
            require(not findings, "passed unit has unresolved findings")
            require((reliable and verdict["answer"] == "pass") or investigated, "pass requires reliable matching verdict or documented investigation")
        elif status == "needs_fix":
            require(bool(findings), "unlocated deduction is not a finding")
            finding_ids = {f["id"] for f in findings}
            require((reliable and verdict["answer"] in finding_ids) or investigated, "fix verdict must identify a finding or have documented investigation")
        else:
            require(bool(unit.get("missingEvidence")), "uncertainty requires missing evidence and next step")
        require(bool(unit["rationale"]), "local rationale required")
    counts = {s: sum(u["status"] == s for u in units) for s in ("pass", "needs_fix", "uncertain")}
    return {
        "reportValid": True,
        "scope": "targeted rules only",
        "units": len(units),
        "statuses": counts,
        "fullCorpusReviewed": False,
        "semanticApproval": "requires primary-source review; structural validation alone gives none",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    try:
        report = json.loads(args.report.read_text())
        summary = validate(report)
        summary["sourceMode"] = "current source"
    except (ValueError, KeyError, TypeError, OSError) as exc:
        print(json.dumps({"reportValid": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(summary, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
