"""Fail when a relative Markdown link or in-repo anchor does not resolve."""
import re
import sys
from pathlib import Path

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
documents = sorted(Path(".").rglob("*.md"))
anchors = {}
for document in documents:
    text = document.read_text(encoding="utf-8")
    ids = set(re.findall(r'<a id="([^"]+)"', text))
    for heading in re.findall(r"^#+\s+(.+)$", text, re.M):
        slug = re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")
        ids.add(slug)
    anchors[document.resolve()] = ids
problems = []
for document in documents:
    prose = re.sub(r"```.*?```", "", document.read_text(encoding="utf-8"), flags=re.S)
    prose = re.sub(r"`[^`\n]*`", "", prose)
    for target in LINK.findall(prose):
        if re.match(r"[a-z]+:", target) or target.startswith("mailto:"):
            continue
        path_part, _, anchor = target.partition("#")
        resolved = (document.parent / path_part).resolve() if path_part else document.resolve()
        if path_part and not resolved.exists():
            problems.append(f"{document}: missing file {target}")
        elif anchor and resolved.suffix == ".md" and anchor not in anchors.get(resolved, set()):
            problems.append(f"{document}: missing anchor {target}")
print("\n".join(problems) or f"{len(documents)} documents, all relative links resolve")
sys.exit(1 if problems else 0)
