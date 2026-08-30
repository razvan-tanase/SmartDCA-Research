#!/usr/bin/env python3
"""Check local targets linked from Markdown files."""

import argparse
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


LINK = re.compile(r"!?\[[^]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+).*?\1")


def markdown_files(paths: list[str]) -> list[tuple[Path, Path]]:
    files: list[tuple[Path, Path]] = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.is_file() and path.suffix == ".md":
            files.append((path, Path(path.name)))
        elif path.is_dir():
            files.extend(
                (candidate, candidate.relative_to(path))
                for candidate in sorted(path.rglob("*.md"))
            )
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="Markdown files or directories to check")
    arguments = parser.parse_args()
    for raw_path in arguments.paths:
        if not Path(raw_path).exists():
            parser.error(f"input path does not exist: {raw_path}")

    failures = 0
    for markdown_file, display_path in markdown_files(arguments.paths):
        fence_character: str | None = None
        fence_length = 0
        for line_number, line in enumerate(
            markdown_file.read_text(encoding="utf-8").splitlines(), start=1
        ):
            fence = FENCE.match(line)
            if fence:
                marker = fence.group(1)
                if fence_character is None:
                    fence_character = marker[0]
                    fence_length = len(marker)
                elif marker[0] == fence_character and len(marker) >= fence_length:
                    fence_character = None
                    fence_length = 0
                continue
            if fence_character is not None:
                continue
            prose = INLINE_CODE.sub("", line)
            for match in LINK.finditer(prose):
                target = match.group(1)
                parsed_target = urlsplit(target)
                if parsed_target.scheme or parsed_target.netloc:
                    continue
                target_path = unquote(parsed_target.path)
                if not (markdown_file.parent / target_path).exists():
                    print(
                        f"{display_path}:{line_number}: "
                        f"missing local target: {target}"
                    )
                    failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
