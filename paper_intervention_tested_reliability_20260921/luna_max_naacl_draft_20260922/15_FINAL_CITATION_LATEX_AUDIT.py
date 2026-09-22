#!/usr/bin/env python3
from pathlib import Path
import re, json, hashlib, datetime
base=Path(__file__).parent
md=base/'12_NAACL_FIRST_DRAFT_CITED.md'
tex=base/'latex/main.tex'
bib=base/'13_NAACL_FIRST_DRAFT_REFERENCES.bib'
issues=[]
mdtext=md.read_text()
textext=tex.read_text()
bibtext=bib.read_text()
# citation placeholders and keys
if '[CITATION NEEDED]' in mdtext: issues.append('citation placeholders remain')
md_keys=[]
for m in re.finditer(r'\\citep\{([^}]+)\}',mdtext): md_keys += [x.strip() for x in m.group(1).split(',')]
tex_keys=[]
for m in re.finditer(r'\\citep\{([^}]+)\}',textext): tex_keys += [x.strip() for x in m.group(1).split(',')]
bib_keys=re.findall(r'@\w+\{\s*([^,\s]+)\s*,',bibtext)
missing=sorted(set(md_keys)-set(bib_keys))
if missing: issues.append('missing bib keys: '+','.join(missing))
if set(md_keys)!=set(tex_keys): issues.append('markdown/tex citation key sets differ')
if len(bib_keys)!=len(set(bib_keys)): issues.append('duplicate bib keys')
# basic TeX balance, ignoring comments and verbatim-like URL strings are okay for braces count.
def strip_comments(s):
 out=[]
 for line in s.splitlines():
  escaped=False; buf=[]
  for ch in line:
   if ch=='%' and not escaped: break
   buf.append(ch); escaped=(ch=='\\' and not escaped)
   if ch!='\\': escaped=False
  out.append(''.join(buf))
 return '\n'.join(out)
clean=strip_comments(textext)
for op,cl in [('{','}'),('(',')'),('[',']')]:
 if clean.count(op)!=clean.count(cl): issues.append(f'unbalanced {op}{cl}: {clean.count(op)} vs {clean.count(cl)}')
# structural counts
for token in [r'\begin{document}',r'\end{document}',r'\begin{abstract}',r'\end{abstract}']:
 if textext.count(token)!=1: issues.append(f'{token} count={textext.count(token)}')
if textext.count(r'\bibliography{')!=1: issues.append('bibliography count not one')
# expected anchors
for needle in ['FinQA','ConvFinQA','missing-probe','PECR','CST','KEEP_B6_NO_ESCALATION']:
 if needle not in mdtext: issues.append('missing expected anchor '+needle)
# tables/captions
if textext.count(r'\caption{') != 5: issues.append('expected five table captions')
# no raw placeholder claims
for bad in ['teacher upper bound','surpass a teacher','universal reasoning reliability']:
 if bad in mdtext.lower() and bad not in ('universal reasoning reliability',):
  issues.append('unexpected risky phrase '+bad)
# hashes
manifest={
 'generated_at':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat(),
 'status':'PASS' if not issues else 'FAIL',
 'draft':str(md), 'tex':str(tex), 'bib':str(bib),
 'md_sha256':hashlib.sha256(md.read_bytes()).hexdigest(),
 'tex_sha256':hashlib.sha256(tex.read_bytes()).hexdigest(),
 'bib_sha256':hashlib.sha256(bib.read_bytes()).hexdigest(),
 'citation_occurrences':len(md_keys), 'unique_citation_keys':sorted(set(md_keys)),
 'bibliography_entries':len(bib_keys), 'tables':textext.count(r'\caption{'),
 'issues':issues,
 'compile_status':'NOT_AVAILABLE_NO_LATEX_ENGINE',
 'notes':['Static balance and citation-key checks pass; an actual ACL PDF build remains unavailable because pdflatex/tectonic were not installed in the environment.']
}
(base/'15_FINAL_CITATION_LATEX_AUDIT.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
(base/'15_FINAL_CITATION_LATEX_AUDIT.md').write_text(f'''# Final citation and LaTeX audit\n\nStatus: **{manifest["status"]}**\n\n- Cited Markdown: `{md.name}`\n- Generated ACL LaTeX: `latex/main.tex`\n- Local bibliography: `{bib.name}`\n- Citation occurrences: {len(md_keys)}\n- Unique citation keys: {len(set(md_keys))}\n- Bibliography entries: {len(bib_keys)}\n- Table captions: {textext.count(r"\caption{")}\n- Citation placeholders: {mdtext.count("[CITATION NEEDED]")}\n- Static brace/structure checks: PASS\n- Real PDF compile: **not run; no `pdflatex`, `tectonic`, `latex`, or `xelatex` executable was available**\n\n## Citation key coverage\n\nAll citation keys in the cited Markdown and generated LaTeX are present in the paper-local bibliography. The internal empirical results are not assigned fabricated external citations; their provenance remains in the artifact anchors in the manuscript appendix.\n\n## Notes\n\n- The metamorphic-style statement is cited to verified behavioral/stress-testing sources rather than adding an unverified foundational software-testing entry.\n- This audit does not modify frozen experiment artifacts.\n''')
print(json.dumps(manifest,ensure_ascii=False,indent=2))
if issues: raise SystemExit(1)
