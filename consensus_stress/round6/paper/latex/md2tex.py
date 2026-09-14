#!/usr/bin/env python3
"""Convert the round-6 paper markdown draft into a NAACL/ACL LaTeX draft.
Handles headings, bold/italic, inline math passthrough, markdown pipe tables, itemize.
Keeps [CITE] placeholders; does NOT invent \\cite keys."""
import re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "../naacl_draft_v4_astra.md"
OUT = sys.argv[2] if len(sys.argv) > 2 else "naacl_main.tex"

def esc_segment(s):
    """Escape LaTeX specials outside $...$ spans, then convert **bold** and *em*."""
    parts = re.split(r"(\$[^$]*\$)", s)
    out = []
    for p in parts:
        if p.startswith("$") and p.endswith("$"):
            out.append(p)  # math passthrough
            continue
        # escape specials first (text-level; math spans are protected)
        for ch, rep in [("\\", "\\textbackslash{}"), ("&", "\\&"), ("%", "\\%"),
                        ("#", "\\#"), ("_", "\\_"), ("{", "\\{"), ("}", "\\}")]:
            p = p.replace(ch, rep)
        # then emphasis on the escaped text
        p = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", p)
        p = re.sub(r"(?<!\*)\*([^*]+?)\*(?!\*)", r"\\emph{\1}", p)
        out.append(p)
    return "".join(out)

def conv_table(rows):
    """rows: list of raw markdown table lines (incl. header sep). Return LaTeX tabular block."""
    # split cells
    def cells(line):
        line = line.strip().strip("|")
        return [c.strip() for c in line.split("|")]
    header = cells(rows[0])
    ncol = len(header)
    body = [cells(r) for r in rows[2:]]
    cols = "l" * ncol
    tex = ["\\begin{table}[t]", "\\centering", "\\small",
           f"\\begin{{tabular}}{{{cols}}}", "\\toprule",
           " & ".join(esc_segment(h) for h in header) + " \\\\",
           "\\midrule"]
    for b in body:
        if len(b) < ncol:
            b = b + [""] * (ncol - len(b))
        tex.append(" & ".join(esc_segment(c) for c in b[:ncol]) + " \\\\")
    tex += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    return "\n".join(tex)

def conv_md(t):
    lines = t.splitlines()
    out = []
    i = 0
    n = len(lines)
    while i < n:
        ln = lines[i]
        # table block: current line starts with | and next line is separator
        if ln.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:\-|]+\|\s*$", lines[i+1]):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            out.append(conv_table(lines[i:j]))
            i = j
            continue
        # headings (normalize inconsistent markdown levels)
        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl = len(m.group(1)); title = m.group(2).strip()
            # strip "Section N — " / "Section N:" prefixes
            title = re.sub(r"^Section \d+\s*[—:]\s*", "", title)
            if lvl == 1:
                sec = "section"
            elif lvl == 2:
                if re.match(r"^\d+\s+[A-Z]", title) or re.match(r"^Abstract$", title):
                    sec = "section"
                else:
                    sec = "subsection"
            elif lvl == 3:
                if re.match(r"^(\d+\.\d+|A\.\d+)\s", title):
                    sec = "subsection"
                else:
                    sec = "subsubsection"
            else:
                sec = "paragraph"
            out.append(f"\\{sec}{{{esc_segment(title)}}}")
            i += 1
            continue
        # itemize
        if ln.strip().startswith("- "):
            out.append("\\begin{itemize}")
            while i < n and lines[i].strip().startswith("- "):
                out.append("  \\item " + esc_segment(lines[i].strip()[2:]))
                i += 1
            out.append("\\end{itemize}")
            continue
        # blank
        if not ln.strip():
            out.append("")
            i += 1
            continue
        # separator
        if re.match(r"^\s*---+\s*$", ln):
            i += 1
            continue
        # normal paragraph
        out.append(esc_segment(ln))
        i += 1
    return "\n".join(out)

def main():
    md = open(SRC, encoding="utf-8").read()
    # start body at "## 1 Introduction" (skip v4 header + Abstract, which go to preamble)
    body_start = md.find("## 1 Introduction")
    if body_start < 0:
        raise SystemExit("## 1 Introduction not found")
    md = md[body_start:]
    body = conv_md(md)
    # extract abstract (between "## Abstract" and "## 1 Introduction")
    am = re.search(r"## Abstract\s*\n(.*?)\n## 1 Introduction", md, re.S)
    abstract = esc_segment(am.group(1).strip()) if am else "(abstract pending)"
    preamble = r"""\documentclass[11pt]{article}

\usepackage[review]{acl}
\usepackage{times}
\usepackage{latexsym}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{graphicx}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{multirow}
\usepackage{url}

\newcommand{\rpi}{R_{\mathrm{PI}}}
\newcommand{\rsq}{\mathrm{RS}_{q}}
\newcommand{\bfq}{\mathrm{BF}_{q}}

\title{When Consensus Lies: Counter-Evidence Responsiveness as a Pre-Outcome Signal of Consensus Error}

\author{Anonymous NAACL submission}

\begin{document}
\maketitle

\begin{abstract}
%s
\end{abstract}
""" % abstract
    post = r"""
% Figures, citation keys, and full reference list are pending.
% Placeholder bibliography (see references.bib for entries once citations are finalized):
\begin{thebibliography}{99}
\bibitem{placeholder} Pending citation completion.
\end{thebibliography}

\end{document}
"""
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(preamble)
        f.write("\n")
        f.write(body)
        f.write("\n")
        f.write(post)
    print(f"written {OUT}")

if __name__ == "__main__":
    main()
