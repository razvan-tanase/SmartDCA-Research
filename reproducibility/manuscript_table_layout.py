"""Apply the institutional 9-point table layout to generated TeX displays."""

import re


def format_manuscript_tables(source: str) -> str:
    """Wrap text columns and headers instead of scaling scientific table text."""
    def format_table(match: re.Match[str]) -> str:
        table = match[0].replace(r"\begin{table}[htbp]", r"\begin{table}[!htbp]")
        table = re.sub(r"\\(?:scriptsize|footnotesize|small|tiny)\b", "", table)
        table = table.replace(r"\centering", r"\centering\fontsize{9}{11}\selectfont\singlespacing", 1)
        table = table.replace("  \\resizebox{\\textwidth}{!}{%\n", "")
        table = table.replace("\\end{tabular}%\n  }", r"\end{tabular}")
        columns = re.search(r"\\begin\{tabular\}\{([lrc]+)\}", table)
        if columns and "l" in columns[1]:
            spec = columns[1].replace("l", r">{\raggedright\arraybackslash}X")
            table = table.replace(columns[0], r"\begin{tabularx}{\textwidth}{" + spec + "}")
            table = table.replace(r"\end{tabular}", r"\end{tabularx}")
        # Each current header occupies the first line after the first horizontal rule.
        before, after = table.split(r"\hline", 1)
        lines = after.splitlines()
        header = lines[1]
        cells = header.rstrip().removesuffix(r"\\").split("&")
        cells = [cell.strip() for cell in cells]
        cells = [r"\shortstack[r]{" + r"\\".join(cell.split()) + "}"
                 if " " in cell and r"\multicolumn" not in cell else cell for cell in cells]
        lines[1] = "    " + " & ".join(cells) + r" \\"
        return before + r"\hline" + "\n".join(lines) + "\n"

    formatted = re.sub(r"\\begin\{table\}.*?\\end\{table\}", format_table, source, flags=re.S)
    return "\n".join(line.rstrip() for line in formatted.splitlines()).rstrip() + "\n"
