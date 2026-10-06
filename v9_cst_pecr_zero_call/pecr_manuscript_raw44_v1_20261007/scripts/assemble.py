from pathlib import Path
import re
P=Path(__file__).resolve().parents[1]
body=(P/'body.tex').read_text();bib=(P/'bibliography_all.tex').read_text()
used=set(k.strip() for match in re.findall(r'\\(?:citep|citet|cite)\{([^}]+)\}',body) for k in match.split(','))
parts=re.split(r'(?=\\bibitem)',bib);kept=[]
for block in parts[1:]:
 m=re.search(r'\]\{([^}]+)\}',block)
 if m and m.group(1) in used:kept.append((m.group(1),block.replace('\\end{thebibliography}','')))
kept.sort();bib=parts[0]+'\n'.join(b for _,b in kept)+'\n\\end{thebibliography}'
assert used==set(k for k,b in kept)
s=(P/'preamble.tex').read_text()+body.replace('% BIBLIOGRAPHY_INSERT',bib)
(P/'main.tex').write_text(s)
# A second file embeds every table for single-file editors.
s=re.sub(r'\\input\{(tables/[^}]+)\}',lambda m:(P/m.group(1)).read_text(),s)
(P/'main_single_file.tex').write_text(s)
print('Assembled manuscript with',len(used),'defined citations.')
