"""Audit integrated manuscript locations, displays, citations, assets, and PDF."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

if __package__:
    from .citation_controls import (
        extract_bibtex_keys, extract_latex_citation_keys, strip_latex_comments,
    )
else:
    from citation_controls import (
        extract_bibtex_keys, extract_latex_citation_keys, strip_latex_comments,
    )


def manuscript_sources(root: Path) -> dict[str, str]:
    """Follow the concrete input graph used by the canonical source."""
    sources: dict[str, str] = {}

    def visit(path: Path) -> None:
        path = path.resolve()
        name = path.relative_to(root.resolve()).as_posix()
        if name in sources:
            raise ValueError(f"repeated or cyclic manuscript input: {name}")
        source = strip_latex_comments(path.read_text(encoding="utf-8"))
        sources[name] = source
        for target in re.findall(r"\\(?:input|include)\{([^}]+)\}", source):
            child = path.parent / target
            visit(child if child.suffix else child.with_suffix(".tex"))

    visit(root / "source/thesis.tex")
    return sources


def audit_sources(root: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    sources = manuscript_sources(root)
    text = "\n".join(sources.values())
    labels = Counter(re.findall(r"\\label\{([^}]+)\}", text))
    errors.extend(f"duplicate label: {label}" for label, n in labels.items() if n != 1)
    references = set(re.findall(r"\\(?:ref|pageref|eqref|autoref)\{([^}]+)\}", text))
    errors.extend(f"unresolved reference: {label}" for label in sorted(references - labels.keys()))

    claims = json.loads((root / "controls/claims.json").read_text())["records"]
    owners: dict[str, list[str]] = {}
    display_prefixes = ("eq:", "thm:", "def:", "fig:", "tab:")
    for claim in claims:
        locations = [claim["manuscript_location"], *claim.get("restatement_locations", [])]
        for location in locations:
            for label in location.split("/"):
                if label not in labels:
                    errors.append(f"{claim['id']}: missing location {label}")
        explicit = claim.get("display_labels", [])
        if len(explicit) != len(set(explicit)):
            errors.append(f"{claim['id']}: repeated display ownership")
        owned = set(explicit) | {
            label for label in claim["manuscript_location"].split("/")
            if label.startswith(display_prefixes)
        }
        for label in owned:
            if label not in labels or not label.startswith(display_prefixes):
                errors.append(f"{claim['id']}: invalid display label {label}")
            owners.setdefault(label, []).append(claim["id"])
    for label in labels:
        if label.startswith(display_prefixes) and len(owners.get(label, [])) != 1:
            errors.append(f"{label}: expected one evidence owner, found {owners.get(label, [])}")

    for kind in ("table", "figure", "equation"):
        for block in re.findall(r"\\begin\{" + kind + r"\}.*?\\end\{" + kind + r"\}", text, re.S):
            block_labels = re.findall(r"\\label\{([^}]+)\}", block)
            if len(block_labels) != 1:
                errors.append(f"{kind}: expected one stable display label")
            elif kind in ("table", "figure") and block_labels[0] not in references:
                errors.append(f"{block_labels[0]}: display is not referred to in prose")
            if kind == "table" and r"\fontsize{9}{11}\selectfont" not in block:
                errors.append(f"{block_labels}: table does not declare template 9-point text")

    cited = extract_latex_citation_keys(text)
    bibliography = (root / "bibliography/references.bib").read_text()
    defined = extract_bibtex_keys(bibliography)
    errors.extend(f"undefined citation: {key}" for key in sorted(cited - defined))
    errors.extend(f"uncited bibliography entry: {key}" for key in sorted(defined - cited))
    body = sources["source/thesis.tex"].split(r"\pagenumbering{arabic}", 1)[1]
    if re.search(r"\[UNRESOLVED:|\b(?:TODO|TBD|FIXME)\b", body):
        errors.append("unresolved manuscript content after front matter")
    return errors, {
        "claim_count": len(claims), "citation_count": len(cited),
        "label_count": len(labels), "display_owners": dict(sorted(owners.items())),
        "source_files": sorted(sources),
        "scope": "Structural coverage and existing chapter audits; semantic completeness requires independent review.",
    }


def reconcile_assets(root: Path) -> list[str]:
    """Regenerate all eight empirical fragments without overwriting accepted bytes."""
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as temporary:
        output = Path(temporary)
        for generator in ("synthetic_evaluation_assets.py", "historical_evaluation_assets.py"):
            result = subprocess.run(
                [sys.executable, str(root.parent / "reproducibility" / generator),
                 "--repository-root", str(root.parent), "--output-directory", str(output)],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                errors.append(f"{generator}: {result.stdout}{result.stderr}")
        fragments = sorted(output.glob("*.tex"))
        if len(fragments) != 8:
            errors.append(f"expected eight regenerated empirical fragments, found {len(fragments)}")
        for path in fragments:
            accepted = root / "generated" / path.name
            if not accepted.is_file() or accepted.read_bytes() != path.read_bytes():
                errors.append(f"generated asset differs: {path.name}")
    return errors


def audit_pdf(build: Path) -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    log = (build / "thesis.log").read_text(errors="replace")
    for line in log.splitlines():
        if any(token in line for token in ("LaTeX Warning:", "Package natbib Warning:",
                                           "Overfull", "Missing character:")):
            errors.append(line)
    xml = subprocess.run(
        ["pdftotext", "-bbox", str(build / "thesis.pdf"), "-"],
        check=True, capture_output=True, text=True,
    ).stdout
    # Legacy TeX math delimiters may map to XML-forbidden control characters.
    # Only bounding boxes are consumed here; glyph appearance is reviewed visually.
    xml = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", xml)
    pages = ET.fromstring(xml).findall(".//{http://www.w3.org/1999/xhtml}page")
    for number, page in enumerate(pages, 1):
        width, height = float(page.attrib["width"]), float(page.attrib["height"])
        if abs(width - 595.276) > 0.5 or abs(height - 841.89) > 0.5:
            errors.append(f"page {number}: page geometry is not A4")
        words = list(page)
        if not words:
            errors.append(f"page {number}: unexpected blank page")
        for word in words:
            if (float(word.attrib["xMin"]) < 0 or float(word.attrib["xMax"]) > width
                    or float(word.attrib["yMin"]) < 0 or float(word.attrib["yMax"]) > height):
                errors.append(f"page {number}: text outside page")
    aux = (build / "thesis.aux").read_text()
    locations = {
        label: {"number": number, "page": page}
        for label, number, page in re.findall(r"\\newlabel\{([^}]+)\}\{\{([^{}]*)\}\{([^{}]*)\}", aux)
    }
    return errors, {"page_count": len(pages), "rendered_locations": locations}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--build-dir", type=Path)
    args = parser.parse_args()
    try:
        errors, receipt = audit_sources(args.root.resolve())
        errors.extend(reconcile_assets(args.root.resolve()))
        if args.build_dir:
            pdf_errors, pdf_receipt = audit_pdf(args.build_dir)
            errors.extend(pdf_errors)
            receipt.update(pdf_receipt)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        errors, receipt = [str(error)], {}
    if errors:
        print("ASSEMBLY CHECK FAILED\n" + "\n".join(errors))
        return 1
    print(f"ASSEMBLY CHECK PASSED: {receipt['claim_count']} claims, "
          f"{len(receipt['display_owners'])} uniquely mapped displays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
