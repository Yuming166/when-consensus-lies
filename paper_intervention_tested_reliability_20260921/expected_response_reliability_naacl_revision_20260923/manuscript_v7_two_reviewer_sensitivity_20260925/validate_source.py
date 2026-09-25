from pathlib import Path
import re
root=Path(__file__).parent
tex=(root/'main.tex').read_text()
bib=(root/'references.bib').read_text()
clean='\n'.join(line.split('%',1)[0] for line in tex.splitlines())
depth=0
for i,ch in enumerate(clean):
    if ch=='{' and (i==0 or clean[i-1] != '\\'): depth+=1
    elif ch=='}' and (i==0 or clean[i-1] != '\\'):
        depth-=1
        if depth<0: raise SystemExit(f'unexpected closing brace near char {i}')
if depth: raise SystemExit(f'unclosed braces: {depth}')
stack=[]
for m in re.finditer(r'\\(begin|end)\{([^}]+)\}',clean):
    kind,name=m.group(1),m.group(2)
    if kind=='begin': stack.append((name,m.start()))
    elif not stack or stack[-1][0]!=name: raise SystemExit(f'mismatched environment end: {name}')
    else: stack.pop()
if stack: raise SystemExit(f'unclosed environments: {stack}')
keys=set(re.findall(r'\\cite(?:p|t)?\{([^}]+)\}',clean))
cites={k.strip() for group in keys for k in group.split(',')}
bibkeys=set(re.findall(r'@\w+\s*\{\s*([^,]+),',bib))
missing=sorted(cites-bibkeys)
if missing: raise SystemExit(f'missing bibliography keys: {missing}')
labels=re.findall(r'\\label\{([^}]+)\}',clean)
refs=re.findall(r'\\(?:ref|pageref|autoref)\{([^}]+)\}',clean)
missing_refs=sorted(set(refs)-set(labels))
if missing_refs: raise SystemExit(f'missing labels: {missing_refs}')
print(f'PASS: braces balanced; environments balanced; {len(cites)} citation keys resolved; {len(set(labels))} labels, {len(set(refs))} references resolved.')
print('NOTE: static checks only. No TeX engine available; compile/PDF/page inspection NOT performed.')
