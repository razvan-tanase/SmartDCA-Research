"""Presentation-only layouts for the generated, unscaled 9-point tables."""

import re


# Percentages include column padding and sum to 100. Explicit widths reserve
# space for labels and prose instead of giving them the residue of wide numeric
# columns. Scientific values and captions remain owned by the asset generators.
TABLE_WIDTHS = {
    "deterministic-primary": (27, 7.5, 12, 12, 12, 9, 10.5, 10),
    "stochastic-primary": (19, 11.5, 5, 12.5, 26, 13.5, 12.5),
    "stochastic-mechanisms": (25, 12, 12, 15, 18, 18),
    "deterministic-coverage-ranges": (14, 26, 17, 17, 13, 13),
    "deterministic-cost-ranges": (22, 24, 17, 17, 20),
    "stochastic-sensitivity": (19, 11.5, 5, 12.5, 26, 13.5, 12.5),
    "stochastic-coverage-diagnostics": (12, 21, 20, 22, 25),
    "synthetic-validation-inventory": (20, 13, 13, 12, 19, 23),
    "historical-primary": (14, 10, 8, 21, 13, 21, 13),
    "historical-comparison-tiers": (8, 22, 7.5, 11, 7.5, 11, 33),
    "historical-policy-mechanisms": (16, 7, 25, 26, 26),
    "historical-risk-attribution": (29, 7, 15, 16, 33),
    "registered-robustness": (20, 20, 6.5, 14, 25, 14.5),
    "historical-cost-robustness": (24, 20, 13, 27, 16),
    "historical-h1-cells": (12, 9.5, 7.5, 6.5, 14, 25, 25.5),
    "historical-h2-cells": (12, 9.5, 7.5, 6.5, 14, 25, 25.5),
    "historical-architecture-cells": (16, 10, 9, 9, 20, 18, 18),
    "historical-monthly-robustness-ranges": (15, 10, 24, 7.5, 12.5, 31),
    "historical-quarterly-robustness-ranges": (15, 10, 24, 7.5, 12.5, 31),
    "historical-evidence-inventory": (18, 13, 12, 11, 19, 12, 15),
}


def format_manuscript_tables(source: str) -> str:
    """Set readable widths, aligned headings, rules, and row/group spacing."""
    def format_table(match: re.Match[str]) -> str:
        table = match[0].replace(r"\begin{table}[htbp]", r"\begin{table}[!htbp]")
        table = re.sub(r"\\(?:scriptsize|footnotesize|small|tiny)\b", "", table)
        table = table.replace(
            r"\centering",
            r"\centering\singlespacing\fontsize{9}{11}\selectfont",
            1,
        )
        table = table.replace("  \\resizebox{\\textwidth}{!}{%\n", "")
        table = table.replace("\\end{tabular}%\n  }", r"\end{tabular}")
        table = re.sub(r" *\\setlength\{\\tabcolsep\}\{[^}]+\}\n", "", table)
        table = re.sub(r" *\\renewcommand\{\\arraystretch\}\{[^}]+\}\n", "", table)
        table = table.replace(
            r"\singlespacing",
            "\\singlespacing\n  \\setlength{\\tabcolsep}{3pt}\n"
            "  \\renewcommand{\\arraystretch}{1.16}",
            1,
        )

        label = re.search(r"\\label\{tab:([^}]+)\}", table)[1]
        widths = TABLE_WIDTHS[label]
        columns = re.search(r"\\begin\{tabular\}\{([lrc]+)\}", table)
        if len(columns[1]) != len(widths) or sum(widths) != 100:
            raise ValueError(f"Invalid manuscript column widths: {label}")
        alignments = {"l": "raggedright", "r": "raggedleft", "c": "centering"}
        spec = "".join(
            rf">{{\{alignments[column]}\arraybackslash}}"
            rf"p{{\dimexpr{width / 100:g}\textwidth-2\tabcolsep\relax}}"
            for column, width in zip(columns[1], widths)
        )
        table = table.replace(columns[0], r"\begin{tabular}{" + spec + "}")

        before, header, body, after = table.split(r"\hline")
        cells = header.strip().removesuffix(r"\\").split("&")
        cells = [cell.strip() for cell in cells]
        # These short display headings keep complete words in narrow columns.
        if label in {"stochastic-primary", "stochastic-sensitivity"}:
            cells[1] = "Policy pair"
        if label in {"historical-h1-cells", "historical-h2-cells"}:
            cells[1] = "Months"
        cells = [
            re.sub(r"(\\multicolumn\{\d+\}\{[^}]+\})\{(.*)\}", r"\1{\\textbf{\2}}", cell)
            if r"\multicolumn" in cell else r"\textbf{" + cell + "}"
            for cell in cells
        ]
        rows = [line.strip() for line in body.splitlines() if line.strip()]
        spaced_rows = []
        for index, row in enumerate(rows):
            spaced_rows.append("    " + row)
            if index + 1 < len(rows):
                group_ends = row.split("&", 1)[0] != rows[index + 1].split("&", 1)[0]
                gap = "4pt" if group_ends else "2pt"
                spaced_rows.append(r"    \addlinespace[" + gap + "]")
        return (
            before + "\\toprule\n    " + " & ".join(cells) + " \\\\\n"
            "    \\midrule\n" + "\n".join(spaced_rows)
            + "\n    \\bottomrule" + after
        )

    formatted = re.sub(r"\\begin\{table\}.*?\\end\{table\}", format_table, source, flags=re.S)
    return "\n".join(line.rstrip() for line in formatted.splitlines()).rstrip() + "\n"
