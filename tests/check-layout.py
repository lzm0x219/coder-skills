"""Check current Skill entries and local Markdown navigation."""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ("master", "design-apis", "fix-bugs", "review-changes", "refactor-code")
EXCLUDED = {".git", "node_modules", "target", ".venv", "__pycache__"}


def heading_text(text: str) -> set[str]:
    counts: Counter[str] = Counter()
    anchors = set()
    for line in text.splitlines():
        anchors.update(re.findall(r'<a\s+(?:id|name)=["\x27]([^"\x27]+)["\x27][^>]*>', line))
        if not re.match(r"^#{1,6} ", line):
            continue
        title = re.sub(r"^#+ ", "", line).lower()
        slug = re.sub(r"[^\w\- ]", "", title).replace(" ", "-")
        count = counts[slug]
        counts[slug] += 1
        anchors.add(slug + (f"-{count}" if count else ""))
    return anchors


def main() -> int:
    failures = []
    for skill in SKILLS:
        entry = ROOT / "skills" / skill / "SKILL.md"
        if not entry.is_file():
            failures.append(f"missing entry: {entry.relative_to(ROOT)}")
            continue
        text = entry.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.S)
        if not frontmatter or not re.search(rf"^name: {re.escape(skill)}$", frontmatter[1], re.M):
            failures.append(f"invalid skill identity: {skill}")
        if not frontmatter or not re.search(r"^description: .+\S$", frontmatter[1], re.M):
            failures.append(f"missing skill description: {skill}")
        if not (ROOT / "tests" / skill / "README.md").is_file():
            failures.append(f"missing suite entry: {skill}")
    checked = 0
    for path in ROOT.rglob("*.md"):
        relative = path.relative_to(ROOT)
        if any(part in EXCLUDED for part in relative.parts):
            continue
        fenced = False
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith(("```", "~~~")):
                fenced = not fenced
                continue
            if fenced:
                continue
            for value in re.findall(r"\[[^\]]*\]\(([^)]+)\)", line):
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", value):
                    continue
                destination, separator, anchor = value.strip("<>").partition("#")
                destination = re.sub(r":\d+$", "", unquote(destination))
                target = (path.parent / destination).resolve() if destination else path
                checked += 1
                error = None
                if not target.exists():
                    error = "missing target"
                elif separator and target.suffix == ".md" and unquote(anchor) not in heading_text(target.read_text(encoding="utf-8")):
                    error = "missing heading"
                if error:
                    failures.append(f"{relative}:{number}: {error}: {value}")
        if fenced:
            failures.append(f"{relative}: unclosed code fence")
    for failure in failures:
        print(f"FAIL: {failure}", file=sys.stderr)
    if failures:
        return 1
    print(f"PASS: {len(SKILLS)} Skill entries and suites; {checked} local navigation links")
    print("LIMIT: external URLs and command execution require separate checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
