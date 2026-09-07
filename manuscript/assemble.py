#!/usr/bin/env python3
"""Produce a content-bound integrated-draft package without granting release approval."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

if __package__:
    from .assembly_controls import audit_pdf, audit_sources
else:
    from assembly_controls import audit_pdf, audit_sources


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def encoded(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def source_inventory(repository: Path) -> tuple[dict[str, dict[str, str | int]], dict[str, object]]:
    """Bind actual source bytes, including staged additions, rather than just HEAD."""
    export = repository / "SOURCE-FILES.json"
    if export.is_file():
        previous = json.loads(export.read_text())
        files = sorted(previous["files"])
        provenance = previous["provenance"]
    else:
        def git(*args: str) -> str:
            return subprocess.run(["git", "-C", str(repository), *args], check=True,
                                  capture_output=True, text=True).stdout.strip()
        files = git("ls-files", "-z").rstrip("\0").split("\0")
        provenance = {"git_head": git("rev-parse", "HEAD"),
                      "working_tree_modified": bool(git("status", "--porcelain"))}
    inventory = {}
    for name in files:
        path = repository / name
        if path.is_symlink() or not path.resolve().is_relative_to(repository.resolve()):
            raise ValueError(f"unsupported source path: {name}")
        inventory[name] = {
            "sha256": digest(path.read_bytes()),
            "mode": 0o755 if path.stat().st_mode & 0o111 else 0o644,
        }
    if export.is_file() and inventory != previous["files"]:
        raise ValueError("exported source no longer matches SOURCE-FILES.json")
    return inventory, provenance


def tool_versions() -> dict[str, str]:
    versions = {"python": sys.version.splitlines()[0]}
    for name, flag in (("pdflatex", "--version"), ("bibtex", "--version"),
                       ("latexmk", "-v"), ("pdftotext", "-v")):
        result = subprocess.run([name, flag], capture_output=True, text=True, check=True)
        versions[name] = (result.stdout + result.stderr).strip()
    return versions


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    repository = root.parent
    output = (args.output_dir or root / "build/packages").resolve()
    try:
        inventory, provenance = source_inventory(repository)
        with tempfile.TemporaryDirectory() as temporary:
            temporary = Path(temporary)
            build = temporary / "build"
            result = subprocess.run(
                [sys.executable, str(root / "build.py"), "--root", str(root),
                 "--output-dir", str(build)], capture_output=True, text=True, check=False,
            )
            if result.returncode:
                raise ValueError(result.stdout + result.stderr)
            errors, audit = audit_sources(root)
            pdf_errors, pdf_audit = audit_pdf(build)
            errors.extend(pdf_errors)
            audit.update(pdf_audit)
            rendered = audit["rendered_locations"]
            for label in audit["display_owners"]:
                if label not in rendered:
                    errors.append(f"display absent from rendered document: {label}")
            if errors:
                raise ValueError("\n".join(errors))
            gate = subprocess.run(
                [sys.executable, str(root / "check_release.py"), "--root", str(root)],
                capture_output=True, text=True, check=False,
            )
            if gate.returncode not in (0, 1):
                raise ValueError("submission checker did not complete: " + gate.stderr)
            contract = json.loads((root / "contract/requirements.json").read_text())
            ready = set(contract["release_gate"]["release_ready_statuses"])
            blockers = [r for r in contract["requirements"] if r.get("release_blocking")
                        and (r.get("status") not in ready or not r.get("value"))]
            claims = json.loads((root / "controls/claims.json").read_text())["records"]
            matrix = io.StringIO(newline="")
            writer = csv.writer(matrix, lineterminator="\n")
            writer.writerow(["claim_id", "wording", "scope", "primary_location", "page",
                             "restatements", "display_labels", "authority_paths", "review_state"])
            for claim in claims:
                label = claim["manuscript_location"].split("/")[-1]
                writer.writerow([claim["id"], claim["wording"], claim["scope"],
                                 claim["manuscript_location"], rendered[label]["page"],
                                 "; ".join(claim.get("restatement_locations", [])),
                                 "; ".join(claim.get("display_labels", [])),
                                 "; ".join(a["path"] for a in claim["authority"]),
                                 claim["review_state"]])
            members = {
                "thesis.pdf": (build / "thesis.pdf").read_bytes(),
                "evidence-map.csv": matrix.getvalue().encode(),
                "assembly-audit.json": encoded(audit),
                "submission-check.txt": (gate.stdout + gate.stderr).encode(),
                "institutional-blockers.json": encoded(blockers),
                "supervisor-review.md": (root / "release/supervisor-review.md").read_bytes(),
                "source/SOURCE-FILES.json": encoded({"files": inventory, "provenance": provenance}),
            }
            for name in inventory:
                members["source/" + name] = (repository / name).read_bytes()
                if (digest(members["source/" + name]) != inventory[name]["sha256"]
                        or (0o755 if (repository / name).stat().st_mode & 0o111 else 0o644)
                        != inventory[name]["mode"]):
                    raise ValueError(f"source changed during assembly: {name}")
            versions = tool_versions()
            members["README.md"] = (
                "# SmartDCA integrated manuscript package\n\n"
                "Complete integrated draft for review. This package does not establish "
                "submission readiness. Read supervisor-review.md and submission-check.txt.\n\n"
                "The source/ directory retains every versioned public repository input. "
                "SOURCE-FILES.json verifies those bytes without requiring Git. Private provider "
                "observations are not part of this repository or package.\n\n"
                "Reproduce from source/ with ./manuscript/assemble-clean.sh (Docker), or with "
                "python manuscript/assemble.py in the declared TeX/Poppler environment. "
                "Different tool versions can change PDF bytes and therefore the identity. "
                "manifest.json binds the source, evidence controls, bibliography, assets, "
                "review brief, audit, and exact PDF. Its identity is SHA-256 of the sorted, "
                "two-space-indented UTF-8 binding JSON plus a final newline.\n"
            ).encode()
            # The payload digest avoids self-referential hashes in the manifest.
            binding = {
                "schema_version": 1, "state": "integrated-draft",
                "submission_gate_passed": gate.returncode == 0,
                "approval": "No candidate transition or human approval is conferred by assembly.",
                "source_sha256": digest(encoded(inventory)),
                "source_provenance": provenance, "tool_versions": versions,
                "files": {name: digest(data) for name, data in sorted(members.items())},
            }
            identity = "smartdca-thesis-integrated-v1-" + digest(encoded(binding))
            manifest = {"identity": identity, "binding": binding}
            members["manifest.json"] = encoded(manifest)
            output.mkdir(parents=True, exist_ok=True)
            archive = output / (identity + ".zip")
            staged = temporary / "package.zip"
            with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as stream:
                for name, data in sorted(members.items()):
                    info = zipfile.ZipInfo(name, (2026, 9, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    mode = inventory.get(name[7:], {}).get("mode", 0o644) if name.startswith("source/") else 0o644
                    info.external_attr = (0o100000 | mode) << 16
                    stream.writestr(info, data)
            if archive.exists() and archive.read_bytes() != staged.read_bytes():
                raise ValueError(f"existing package differs at the same identity: {archive}")
            shutil.copyfile(staged, archive)
            for name in ("thesis.pdf", "manifest.json", "evidence-map.csv", "assembly-audit.json",
                         "submission-check.txt", "institutional-blockers.json", "supervisor-review.md"):
                destination = output / identity / name
                destination.parent.mkdir(exist_ok=True)
                destination.write_bytes(members[name])
            print(f"PACKAGE ASSEMBLED: {archive}\nSTATE: integrated-draft\n"
                  f"SUBMISSION GATE: {'passed' if gate.returncode == 0 else 'blocked'}\n"
                  f"PDF: {audit['page_count']} pages")
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(f"ASSEMBLY FAILED: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
