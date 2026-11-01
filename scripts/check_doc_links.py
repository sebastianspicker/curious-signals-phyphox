#!/usr/bin/env python3
"""Fail when tracked Markdown links to a path the repository does not contain.

Readers browse these files on GitHub or in a clone, so a relative link into an
ignored build directory such as ``output/`` is dead for them. Fenced code
blocks and external URLs are not checked.
"""

from __future__ import annotations

import os
import posixpath
import re
import subprocess
import sys
from urllib.parse import unquote, urlsplit

LINKS = (
    re.compile(r"\]\((<[^>]+>|[^)\s]+)"),  # inline [text](target) and [text](<target>)
    re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE),  # [ref]: target
    re.compile(r"""\b(?:href|src)=["']([^"']+)["']"""),  # inline HTML
)
FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,}).*?^[ \t]*\1", re.DOTALL | re.MULTILINE)


def tracked_files() -> list[str]:
    result = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True, text=True)
    return [name for name in result.stdout.split("\0") if name]


def broken_links(files: list[str]) -> list[str]:
    tracked = {name for name in files if os.path.exists(name)}
    folders = set()
    for name in files:
        folder = posixpath.dirname(name)
        while folder:
            folders.add(folder)
            folder = posixpath.dirname(folder)
    folders.add(".")
    problems = []
    for name in files:
        # A tracked file deleted in the working tree has no text to check.
        if not name.endswith(".md") or not os.path.isfile(name):
            continue
        with open(name, encoding="utf-8") as handle:
            text = FENCE.sub("", handle.read())
        for match in (m for pattern in LINKS for m in pattern.finditer(text)):
            url = urlsplit(match.group(1).strip("<>"))
            if url.scheme or url.netloc or not url.path:
                continue
            path = unquote(url.path)
            # GitHub resolves a leading slash from the repository root.
            base = "" if path.startswith("/") else posixpath.dirname(name)
            target = posixpath.normpath(posixpath.join(base, path.lstrip("/")))
            if target not in tracked and target not in folders:
                problems.append(f"{name}: link to untracked path {match.group(1)}")
    return problems


def main() -> int:
    problems = broken_links(tracked_files())
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"{len(problems)} Markdown links point outside the tracked tree.", file=sys.stderr)
        return 1
    print("Markdown links resolve to tracked files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
