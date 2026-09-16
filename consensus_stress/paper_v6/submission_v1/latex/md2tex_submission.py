#!/usr/bin/env python3
"""Convert the Paper v6 Markdown draft into an ACL/NAACL LaTeX manuscript.

This is an improved, local conversion script based on the round-6 converter.  It
is intentionally conservative:

* the integrated v6 Markdown draft is the canonical input;
* the front-matter/editorial source-map material is not typeset in the paper;
* verified raw ``\\citep{...}`` commands are preserved verbatim;
* no citation key or bibliography entry is synthesized;
* inline and display LaTeX math is protected before text escaping;
* Markdown tables become width-aware ``tabularx`` tables with captions; and
* the copied ACL style/BST files are never edited by this script.

The script has no third-party dependencies.  Run it from this directory, or
pass explicit source/output paths.
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

HERE = Path(__file__).resolve().parent
DEFAULT_SOURCE = HERE.parent / "manuscript.md"
DEFAULT_OUTPUT = HERE / "main.tex"

# Keep the replacement ASCII where possible.  Math-like Unicode characters are
# converted to short inline math fragments after existing math/code spans have
# been protected, so they cannot corrupt an existing equation.
UNICODE_REPLACEMENTS = {
    "—": "---",
    "–": "--",
    "−": "-",
    "‑": "-",
    "’": "'",
    "‘": "`",
    "“": "``",
    "”": "''",
    "…": "...",
    "×": "$\\times$",
    "→": "$\\to$",
    "←": "$\\leftarrow$",
    "↔": "$\\leftrightarrow$",
    "≈": "$\\approx$",
    "≤": "$\\leq$",
    "≥": "$\\geq$",
    "≪": "$\\ll$",
    "Δ": "$\\Delta$",
    "ρ": "$\\rho$",
    "±": "$\\pm$",
}

# Text-level escaping is deliberately character based.  In particular, do not
# escape the braces/backslashes introduced by a previous replacement.
LATEX_TEXT_ESCAPES = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}

# Inline/display math forms used in the Markdown draft.  Display math is
# handled as a separate block when it occupies a whole line, but ``\\[...\\]``
# also occurs inline in ordinary paragraphs and must be protected before text
# escaping.
INLINE_MATH_RE = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]|\$[^$\n]*\$", re.DOTALL)
CODE_SPAN_RE = re.compile(r"`([^`\n]+)`")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
ULIST_RE = re.compile(r"^\s*[-*+]\s+(.*)$")
OLIST_RE = re.compile(r"^\s*\d+[.)]\s+(.*)$")
TABLE_SEPARATOR_RE = re.compile(r"^\s*\|\s*:?-{1,}:?\s*(?:\|\s*:?-{1,}:?\s*)+\|?\s*$")
CAPTION_RE = re.compile(r"^\s*\*\*(Table\s+\d+\s*:\s*.*?)\*\*\s*$", re.IGNORECASE)
RAW_LATEX_RE = re.compile(r"\\(?:citep|citet|citeauthor|citeyear)\{[^{}\n]+\}")


@dataclass
class ConversionStats:
    source_lines: int = 0
    output_lines: int = 0
    headings: int = 0
    paragraphs: int = 0
    blockquotes: int = 0
    itemize_blocks: int = 0
    enumerate_blocks: int = 0
    tables: int = 0
    equations: int = 0
    citations_preserved: int = 0
    ref_lines_omitted: int = 0
    editorial_lines_omitted: int = 0
    captioned_tables: int = 0
    heading_names: list[str] = field(default_factory=list)


@dataclass
class ProtectedText:
    text: str
    spans: list[str]


def protect_spans(text: str, marker_prefix: str = "ZZZCSTSPAN") -> ProtectedText:
    """Protect code and LaTeX spans so text escaping cannot alter them.

    ``marker_prefix`` lets callers run a second protection pass without
    colliding with placeholders emitted by an earlier pass.
    """
    spans: list[str] = []

    def save(match: re.Match[str]) -> str:
        spans.append(match.group(0))
        return f"{marker_prefix}{len(spans) - 1}ZZZ"

    # Code first prevents dollar signs inside a code span from becoming math.
    text = CODE_SPAN_RE.sub(save, text)
    text = INLINE_MATH_RE.sub(save, text)
    # Preserve verified citation commands as raw LaTeX rather than escaping the
    # backslash/braces into text.
    text = RAW_LATEX_RE.sub(save, text)
    return ProtectedText(text=text, spans=spans)


def restore_spans(text: str, spans: Sequence[str]) -> str:
    for idx, value in enumerate(spans):
        text = text.replace(f"ZZZCSTSPAN{idx}ZZZ", value)
    return text


def normalize_unicode(text: str) -> str:
    for source, replacement in UNICODE_REPLACEMENTS.items():
        text = text.replace(source, replacement)
    return text


CODE_UNICODE_REPLACEMENTS = {
    "—": "---", "–": "--", "−": "-", "‑": "-",
    "’": "'", "‘": "'", "“": '"', "”": '"', "…": "...",
    "×": "x", "→": "->", "←": "<-", "↔": "<->",
    "≈": "~", "≤": "<=", "≥": ">=", "≪": "<<",
    "Δ": "Delta", "ρ": "rho", "±": "+/-",
}


def normalize_code(text: str) -> str:
    for source, replacement in CODE_UNICODE_REPLACEMENTS.items():
        text = text.replace(source, replacement)
    return text


def escape_text(text: str) -> str:
    # Protect source code, existing math, and raw citation commands first.
    # Unicode normalization can introduce new math fragments (for example,
    # ``→`` becomes ``$\\to$``); protect those fragments in a second pass so
    # their backslashes are not escaped as literal text.
    protected = protect_spans(text)
    normalized = normalize_unicode(protected.text)
    normalized_protected = protect_spans(normalized, marker_prefix="ZZZCSTGEN")
    escaped = "".join(
        LATEX_TEXT_ESCAPES.get(ch, ch) for ch in normalized_protected.text
    )

    # Markdown emphasis is applied after escaping.  This keeps the braces and
    # backslashes belonging to the generated LaTeX commands untouched.
    escaped = re.sub(
        r"\*\*(.+?)\*\*",
        lambda m: r"\textbf{" + m.group(1) + "}",
        escaped,
    )
    escaped = re.sub(
        r"(?<!\*)\*([^*\n]+?)\*(?!\*)",
        lambda m: r"\emph{" + m.group(1) + "}",
        escaped,
    )

    # Restore math fragments introduced by Unicode normalization first.
    # They were protected by the second pass and must remain raw LaTeX.
    for idx, value in enumerate(normalized_protected.spans):
        marker = f"ZZZCSTGEN{idx}ZZZ"
        escaped = escaped.replace(marker, value)

    # Permit line breaks after escaped underscores in ordinary text.  This is
    # especially useful for protocol identifiers such as ``TARGET_SPEC`` in
    # narrow tabularx cells; it does not change the rendered glyphs.
    escaped = escaped.replace(r"\_", r"\_\allowbreak{}")

    # Restore source spans.  Code contents were not escaped above because they
    # were placeholders; escape them now, but do not interpret Markdown
    # emphasis inside code.  Repository paths use ``\path`` so url.sty can
    # break them at slashes, dots, and other legal path boundaries.
    for idx, value in enumerate(protected.spans):
        marker = f"ZZZCSTSPAN{idx}ZZZ"
        if value.startswith("`"):
            code = normalize_code(value[1:-1])
            if "/" in code:
                replacement = r"\path{" + code + "}"
            else:
                code = "".join(LATEX_TEXT_ESCAPES.get(ch, ch) for ch in code)
                replacement = r"\texttt{" + code + "}"
        else:
            replacement = value
        escaped = escaped.replace(marker, replacement)
    return escaped


def strip_inline_code_for_heading(text: str) -> str:
    # Headings in this draft do not use code spans, but this keeps heading
    # commands robust if a future title contains one.
    return text


def heading_depth(title: str, markdown_level: int) -> int:
    """Return the LaTeX sectioning depth using numeric prefixes when present."""
    match = re.match(r"^(\d+(?:\.\d+)*)\.?\s+", title)
    if match:
        return min(match.group(1).count(".") + 1, 4)
    if markdown_level <= 1:
        return 1
    return min(markdown_level, 4)


def clean_heading_title(title: str) -> str:
    title = re.sub(r"^Section\s+\d+\s*[—:-]\s*", "", title, flags=re.IGNORECASE)
    title = re.sub(r"^\d+(?:\.\d+)*\.?\s+", "", title)
    return title.strip()


def latex_heading(title: str, markdown_level: int, stats: ConversionStats) -> str:
    # Determine the semantic depth before stripping the numeric prefix.
    depth = heading_depth(title, markdown_level)
    title = clean_heading_title(title)
    commands = {1: "section", 2: "subsection", 3: "subsubsection", 4: "paragraph"}
    command = commands[depth]
    stats.headings += 1
    stats.heading_names.append(title)
    rendered = escape_text(title)
    # Keep math in the visible heading while supplying plain text to
    # hyperref's PDF bookmark generator.  This avoids harmless but noisy
    # ``Token not allowed in a PDF string`` warnings under review builds.
    if r"\(" in title or r"\[" in title:
        pdf_title = title
        pdf_title = re.sub(r"\\\(|\\\)", "", pdf_title)
        pdf_title = re.sub(r"\\\[|\\\]", "", pdf_title)
        pdf_title = pdf_title.replace(r"\times", "x")
        pdf_title = pdf_title.replace("_", r"\_")
        return f"\\{command}{{\\texorpdfstring{{{rendered}}}{{{pdf_title}}}}}"
    return f"\\{command}{{{rendered}}}"


def split_table_row(line: str) -> list[str]:
    """Split a Markdown pipe row, ignoring pipes inside math/code spans."""
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|") and not raw.endswith("\\|"):
        raw = raw[:-1]

    cells: list[str] = []
    current: list[str] = []
    i = 0
    in_code = False
    math_delim: str | None = None
    while i < len(raw):
        if raw[i] == "`":
            in_code = not in_code
            current.append(raw[i])
            i += 1
            continue
        if not in_code:
            if math_delim is None and raw.startswith(r"\(", i):
                math_delim = r"\)"
            elif math_delim == r"\)" and raw.startswith(r"\)", i):
                math_delim = None
            elif math_delim is None and raw[i] == "$":
                math_delim = "$"
            elif math_delim == "$" and raw[i] == "$":
                math_delim = None
        if raw[i] == "|" and not in_code and math_delim is None:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(raw[i])
        i += 1
    cells.append("".join(current).strip())
    return cells


def is_table_start(lines: Sequence[str], index: int) -> bool:
    return (
        index + 1 < len(lines)
        and lines[index].strip().startswith("|")
        and bool(TABLE_SEPARATOR_RE.match(lines[index + 1]))
    )


def table_column_spec(separator: str) -> str:
    cells = split_table_row(separator)
    specs: list[str] = []
    for cell in cells:
        cell = cell.strip()
        left = cell.startswith(":")
        right = cell.endswith(":")
        if left and right:
            specs.append(r">{\centering\arraybackslash}X")
        elif right:
            specs.append(r">{\raggedleft\arraybackslash}X")
        else:
            specs.append(r">{\raggedright\arraybackslash}X")
    return "@{}" + "".join(specs) + "@{}"


def escape_table_cell(text: str) -> str:
    """Escape a table cell and add content-neutral breakpoints.

    Narrow ACL columns otherwise treat compact tokens such as ``HC=96/wrong=8``
    as a single unbreakable word.  The discretionary breaks do not alter the
    visible text or any reported value.
    """
    rendered = escape_text(text)
    for token in ("=", "/", ";", "-"):
        rendered = rendered.replace(token, token + r"\allowbreak{}")
    # These long words can exceed a narrow X column before TeX gets a chance
    # to hyphenate them.  The discretionary breaks preserve their glyphs.
    rendered = rendered.replace("Interpretation", r"Inter\allowbreak{}pretation")
    rendered = rendered.replace("Exploratory", r"Explor\allowbreak{}atory")
    rendered = rendered.replace("Qwen3.5-", r"Qwen3.5\allowbreak{}-")
    return rendered


def render_table(rows: Sequence[str], caption: str | None, table_number: int, stats: ConversionStats) -> str:
    header = split_table_row(rows[0])
    body = [split_table_row(row) for row in rows[2:]]
    ncol = len(header)
    spec = table_column_spec(rows[1])
    lines = [
        r"\begin{table}[t]",
        r"\centering",
        r"\small",
    ]
    if caption:
        caption_number = re.search(r"Table\s+(\d+)", caption, flags=re.IGNORECASE)
        caption_text = re.sub(r"^Table\s+\d+\s*:\s*", "", caption, flags=re.IGNORECASE)
        lines.append(f"\\caption{{{escape_text(caption_text)}}}")
        label = f"tab:table{caption_number.group(1)}" if caption_number else f"tab:cst{table_number}"
        lines.append(f"\\label{{{label}}}")
    lines.extend([
        f"\\begin{{tabularx}}{{\\columnwidth}}{{{spec}}}",
        r"\toprule",
        " & ".join(escape_table_cell(cell) for cell in header) + r" \\",
        r"\midrule",
    ])
    for row in body:
        row = list(row[:ncol]) + [""] * max(0, ncol - len(row))
        lines.append(" & ".join(escape_table_cell(cell) for cell in row[:ncol]) + r" \\")
    lines.extend([r"\bottomrule", r"\end{tabularx}", r"\end{table}", ""])
    stats.tables += 1
    if caption:
        stats.captioned_tables += 1
    return "\n".join(lines)


def extract_abstract(lines: Sequence[str]) -> list[str]:
    start = next((i for i, line in enumerate(lines) if line.strip().lower() == "## abstract"), None)
    if start is None:
        return []
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].strip().lower() == "## 1 introduction"),
        len(lines),
    )
    return list(lines[start + 1 : end])


def find_body_start(lines: Sequence[str]) -> int:
    for i, line in enumerate(lines):
        if re.match(r"^##\s+1\s+Introduction\s*$", line.strip(), flags=re.IGNORECASE):
            return i
    raise ValueError("canonical draft does not contain '## 1 Introduction'")


def is_editorial_heading(title: str) -> bool:
    normalized = title.strip().casefold()
    return normalized.startswith("(ref)") or normalized.startswith("bounded-claims note")


def filtered_body(lines: Sequence[str], stats: ConversionStats) -> list[str]:
    """Drop only editorial source-map sections and standalone (ref:) records."""
    start = find_body_start(lines)
    result: list[str] = []
    skip_editorial = False
    skip_level = 0
    for line in lines[start:]:
        heading = HEADING_RE.match(line)
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if skip_editorial:
                if level <= skip_level:
                    skip_editorial = False
                else:
                    stats.editorial_lines_omitted += 1
                    continue
            if is_editorial_heading(title):
                skip_editorial = True
                skip_level = level
                stats.editorial_lines_omitted += 1
                continue
        if skip_editorial:
            stats.editorial_lines_omitted += 1
            continue
        if line.strip().startswith("(ref"):
            stats.ref_lines_omitted += 1
            continue
        result.append(line)
    return result


def is_blank(line: str) -> bool:
    return not line.strip()


def is_display_math_start(line: str) -> bool:
    return line.strip() == r"\["


def is_display_math_end(line: str) -> bool:
    return line.strip() == r"\]"


def render_list(lines: Sequence[str], index: int, stats: ConversionStats) -> tuple[str, int]:
    first = lines[index]
    ordered = bool(OLIST_RE.match(first))
    matcher = OLIST_RE if ordered else ULIST_RE
    items: list[str] = []
    i = index
    while i < len(lines):
        match = matcher.match(lines[i])
        if not match:
            break
        item_lines = [match.group(1).strip()]
        i += 1
        # Allow wrapped, indented continuation lines without swallowing the
        # next paragraph or a structural block.
        while i < len(lines):
            candidate = lines[i]
            if is_blank(candidate) or HEADING_RE.match(candidate) or is_table_start(lines, i):
                break
            if ULIST_RE.match(candidate) or OLIST_RE.match(candidate) or candidate.lstrip().startswith(">"):
                break
            if is_display_math_start(candidate):
                break
            if candidate.startswith(("  ", "\t")):
                item_lines.append(candidate.strip())
                i += 1
            else:
                break
        items.append(" ".join(item_lines))
    environment = "enumerate" if ordered else "itemize"
    if ordered:
        stats.enumerate_blocks += 1
    else:
        stats.itemize_blocks += 1
    rendered = [f"\\begin{{{environment}}}"]
    rendered.extend(f"  \\item {escape_text(item)}" for item in items)
    rendered.append(f"\\end{{{environment}}}")
    return "\n".join(rendered) + "\n", i


def render_quote(lines: Sequence[str], index: int, stats: ConversionStats) -> tuple[str, int]:
    quote_lines: list[str] = []
    i = index
    while i < len(lines) and lines[i].lstrip().startswith(">"):
        quote_lines.append(re.sub(r"^\s*>\s?", "", lines[i]).strip())
        i += 1
    stats.blockquotes += 1
    return "\\begin{quote}\n" + escape_text(" ".join(quote_lines)) + "\n\\end{quote}\n", i


def render_blocks(lines: Sequence[str], stats: ConversionStats) -> str:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if is_blank(line):
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line):
            i += 1
            continue
        heading = HEADING_RE.match(line)
        if heading:
            out.append(latex_heading(heading.group(2), len(heading.group(1)), stats))
            out.append("")
            i += 1
            continue
        if is_table_start(lines, i):
            table_end = i + 2
            while table_end < len(lines) and lines[table_end].strip().startswith("|"):
                table_end += 1
            caption: str | None = None
            next_index = table_end
            caption_index = table_end
            while caption_index < len(lines) and is_blank(lines[caption_index]):
                caption_index += 1
            if caption_index < len(lines):
                caption_match = CAPTION_RE.match(lines[caption_index])
                if caption_match:
                    caption = caption_match.group(1).strip()
                    next_index = caption_index + 1
            out.append(render_table(lines[i:table_end], caption, stats.tables + 1, stats))
            i = next_index
            continue
        if is_display_math_start(line):
            j = i + 1
            while j < len(lines) and not is_display_math_end(lines[j]):
                j += 1
            if j >= len(lines):
                raise ValueError(f"unterminated display math beginning at source line {i + 1}")
            out.extend(lines[i : j + 1])
            out.append("")
            stats.equations += 1
            i = j + 1
            continue
        if ULIST_RE.match(line) or OLIST_RE.match(line):
            rendered, i = render_list(lines, i, stats)
            out.append(rendered)
            continue
        if line.lstrip().startswith(">"):
            rendered, i = render_quote(lines, i, stats)
            out.append(rendered)
            continue

        # Ordinary Markdown paragraph: join wrapped source lines, while keeping
        # all inline math, [CITE] markers, and emphasis content intact.
        paragraph_lines = [line.strip()]
        i += 1
        while i < len(lines):
            candidate = lines[i]
            if (
                is_blank(candidate)
                or HEADING_RE.match(candidate)
                or is_table_start(lines, i)
                or is_display_math_start(candidate)
                or ULIST_RE.match(candidate)
                or OLIST_RE.match(candidate)
                or candidate.lstrip().startswith(">")
                or re.match(r"^\s*---+\s*$", candidate)
            ):
                break
            paragraph_lines.append(candidate.strip())
            i += 1
        out.append(escape_text(" ".join(paragraph_lines)))
        out.append("")
        stats.paragraphs += 1
    return "\n".join(out).rstrip() + "\n"


def render_abstract(lines: Sequence[str], stats: ConversionStats) -> str:
    # Abstract is a small paragraph block, but using the same renderer keeps
    # math/emphasis handling consistent with the body.
    return render_blocks(lines, stats).strip()


def document_preamble(title: str, abstract: str, stats: ConversionStats) -> str:
    return rf"""\documentclass[11pt]{{article}}

% Copied unchanged from consensus_stress/round6/paper/latex/acl.sty.
\usepackage[review]{{acl}}
\usepackage{{times}}
\usepackage{{latexsym}}
\usepackage{{amsmath,amssymb}}
\usepackage{{booktabs}}
\usepackage{{graphicx}}
\usepackage{{microtype}}
\usepackage{{array}}
\usepackage{{tabularx}}
\usepackage{{multirow}}
\usepackage{{url}}
\urlstyle{{tt}}
\usepackage[utf8]{{inputenc}}

\newcommand{{\rsq}}{{\mathrm{{RS}}_q}}
\newcommand{{\bfq}}{{\mathrm{{BF}}_q}}
\newcommand{{\snatural}}{{S_{{\mathrm{{natural}}}}}}
\newcommand{{\sind}}{{S_{{\mathrm{{ind}}}}}}

\title{{{escape_text(title)}}}
\author{{Anonymous NAACL submission}}

\begin{{document}}
\maketitle

\begin{{abstract}}
{abstract}
\end{{abstract}}

% Generated by md2tex_submission.py from the reconciled submission Markdown.
% Verified citation commands preserved: {stats.citations_preserved}.
% Bibliography keys come from ../references.bib; no key is synthesized by this converter.
"""


def document_postamble() -> str:
    return r"""
\bibliography{../references}

\end{document}
"""


def convert(source: Path, output: Path) -> ConversionStats:
    markdown = source.read_text(encoding="utf-8")
    lines = markdown.splitlines()
    stats = ConversionStats(source_lines=len(lines), citations_preserved=len(re.findall(r"\\citep\{", markdown)))
    abstract_lines = extract_abstract(lines)
    body_lines = filtered_body(lines, stats)
    abstract = render_abstract(abstract_lines, stats)
    body = render_blocks(body_lines, stats)
    title = "CST-Bench: Measuring Consensus Reliability with Direction-Gated Natural-Pair Stress Tests"
    document = document_preamble(title, abstract, stats) + "\n" + body + document_postamble()
    output.write_text(document, encoding="utf-8")
    stats.output_lines = len(document.splitlines())
    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("output", nargs="?", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = convert(args.source, args.output)
    print(f"written {args.output}")
    print(
        "stats: "
        f"source_lines={stats.source_lines} output_lines={stats.output_lines} "
        f"headings={stats.headings} paragraphs={stats.paragraphs} "
        f"tables={stats.tables} captioned_tables={stats.captioned_tables} "
        f"equations={stats.equations} citations_preserved={stats.citations_preserved} "
        f"ref_lines_omitted={stats.ref_lines_omitted} "
        f"editorial_lines_omitted={stats.editorial_lines_omitted}"
    )


if __name__ == "__main__":
    main()
