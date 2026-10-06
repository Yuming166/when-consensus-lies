"""Native SVG revision of the author's figure, with source-verified Arithmetic44."""
from pathlib import Path
import copy
import hashlib
import json
import math
import os
import subprocess
import sys

from lxml import etree as E

ROOT = Path(__file__).resolve().parent
BASE = ROOT.parent
RENDER = BASE / 'pecr_method_phenomenon_features_v7_20261005'
sys.path.insert(0, str(RENDER / '.render_deps'))
os.environ['FONTCONFIG_FILE'] = str(RENDER / 'FONTCONFIG.xml')
import cairosvg
import matplotlib
matplotlib.use('Agg')
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path as MPath
from matplotlib.textpath import TextPath
matplotlib.rcParams['mathtext.fontset'] = 'stix'

SVG = 'http://www.w3.org/2000/svg'
NS = {'s': SVG}
SOURCE = ROOT / 'source/user_method_v4.svg'
SCHEMA = BASE / 'pecr_two_track_benchmark_release_v2_20261007/schemas/feature_schema.json'
EXTRACTOR = BASE / 'pecr_deepseek_v41_flash_report_oof_v1_20261006/src/arithmetic.py'
schema = json.loads(SCHEMA.read_text())
assert schema['Arithmetic44']['groups'] == {
    'worldwise_alignment': [0, 24], 'cross_world_consistency': [24, 40],
    'question_operation_cues': [40, 44]}
assert schema['world_order'] == ['original', 'positive', 'negative']
assert schema['constructed_views']['raw_plus_arithmetic44']['dim'] == 158
assert schema['constructed_views']['raw']['dim'] == 114

tree = E.parse(str(SOURCE))
root = tree.getroot()
root.set('width', '218.27pt')
root.set('height', '507pt')
# Resolve Illustrator PostScript family aliases for portable Arial/Courier rendering.
for style in root.iter(f'{{{SVG}}}style'):
    style.text=style.text.replace('ArialMT, Arial','Arial').replace('Arial-BoldMT, Arial','Arial')
    style.text=style.text.replace("CourierNewPSMT, 'Courier New'", "'Courier New'").replace("CourierNewPS-BoldMT, 'Courier New'", "'Courier New'")
original_preserved = E.tostring(root.xpath('//*[@id="preserved_user_objects"]')[0])
original_risk = copy.deepcopy(root.xpath('//*[@id="risk_panel"]')[0])
P = dict(blue='#D9E8FB', pink='#F7CECC', yellow='#FFF5C4',
         cyan='#9FCEFC', purple='#E2D5E7', white='#FFFFFF')
sequence = 0
text_bounds = []

def element(kind, parent=None, **attrs):
    global sequence
    sequence += 1
    e = E.SubElement(panel if parent is None else parent, f'{{{SVG}}}{kind}')
    e.set('id', f'raw44_{sequence}')
    for k, v in attrs.items():
        e.set(k.replace('_', '-'), str(v))
    return e

def rect(x, y, w, h, color='white', radius=2, lw=.5, dash=False, parent=None):
    attrs = dict(x=x, y=y, width=w, height=h, rx=radius, ry=radius,
                 fill=P.get(color, color), stroke='black', stroke_width=lw)
    if dash:
        attrs['stroke_dasharray'] = '2 1.3'
    return element('rect', parent, **attrs)

def line(points, lw=.5, dash=False, parent=None):
    attrs = dict(points=' '.join(f'{x},{y}' for x, y in points), fill='none',
                 stroke='black', stroke_width=lw, stroke_linejoin='round', stroke_linecap='round')
    if dash:
        attrs['stroke_dasharray'] = '2 1.3'
    return element('polyline', parent, **attrs)

def arrow(points, lw=.5, dash=False, head=1.65, parent=None):
    line(points, lw, dash, parent)
    x, y = points[-1]
    px, py = points[-2]
    dx, dy = x-px, y-py
    norm = math.hypot(dx, dy)
    dx, dy = dx/norm, dy/norm
    return element('polygon', parent, points=(
        f'{x},{y} {x-head*dx-head*.42*dy},{y-head*dy+head*.42*dx} '
        f'{x-head*dx+head*.42*dy},{y-head*dy-head*.42*dx}'), fill='black')

font_root = RENDER/'fonts'
font_files = {p.name.lower(): p for p in font_root.rglob('*') if p.suffix.lower()=='.ttf'}

def text(x, y, s, size=5.2, bold=False, anchor='start', mono=False, parent=None, max_width=None):
    fname = ('courbd.ttf' if bold else 'cour.ttf') if mono else ('arialbd.ttf' if bold else 'arial.ttf')
    prop = FontProperties(fname=str(font_files[fname])) if fname in font_files else FontProperties(family='Arial', weight='bold' if bold else 'normal')
    path = TextPath((0, 0), s, size=size, prop=prop, usetex=False)
    b = path.get_extents()
    if max_width and b.width > max_width:
        size *= max_width/b.width
        path = TextPath((0, 0), s, size=size, prop=prop, usetex=False)
        b = path.get_extents()
    offset = b.width/2 if anchor == 'middle' else b.width if anchor == 'end' else 0
    text_bounds.append(dict(text=s, bounds=[x-offset, y-b.y1, x-offset+b.width, y-b.y0], font_size=size))
    e = element('text', parent, x=x, y=y, fill='black', font_family='Courier New' if mono else 'Arial',
                font_size=size, font_weight='700' if bold else '400', text_anchor=anchor)
    e.text = s
    return e

def formula(x, y, s, size=7, parent=None, max_width=None):
    p = TextPath((0, 0), '$'+s+'$', size=size, prop=FontProperties(family='STIXGeneral'), usetex=False)
    b = p.get_extents()
    if max_width and b.width > max_width:
        size *= max_width/b.width
        p = TextPath((0, 0), '$'+s+'$', size=size, prop=FontProperties(family='STIXGeneral'), usetex=False)
        b = p.get_extents()
    commands = []
    for v, c in p.iter_segments(curves=True):
        if c == MPath.MOVETO: commands.append(f'M{v[0]:.5f},{v[1]:.5f}')
        elif c == MPath.LINETO: commands.append(f'L{v[0]:.5f},{v[1]:.5f}')
        elif c == MPath.CURVE3: commands.append('Q'+','.join(f'{n:.5f}' for n in v))
        elif c == MPath.CURVE4: commands.append('C'+','.join(f'{n:.5f}' for n in v))
        elif c == MPath.CLOSEPOLY: commands.append('Z')
    e = element('path', parent, d=' '.join(commands), fill='black',
                transform=f'translate({x-b.x0-b.width/2:.5f} {y:.5f}) scale(1 -1)', aria_label=s)
    text_bounds.append(dict(formula=s, bounds=[x-b.width/2, y-b.y1, x+b.width/2, y-b.y0], font_size=size))
    return e

def circle(x,y,r,color='white',parent=None,lw=.4):
    return element('circle',parent,cx=x,cy=y,r=r,fill=P.get(color,color),stroke='black',stroke_width=lw)

def table_icon(x,y):
    rect(x+1.5,y-1.5,13,12,'purple',1,.4)
    rect(x+.75,y-.75,13,12,'yellow',1,.4)
    rect(x,y,13,12,'white',1,.5)
    rect(x+4.4,y+4.1,4,3.6,'pink',.4,.2)
    rect(x+8.6,y+8,4,3.6,'blue',.4,.2)
    for dx in [4.3,8.6]:line([(x+dx,y),(x+dx,y+12)],.3)
    for dy in [4,8]:line([(x,y+dy),(x+13,y+dy)],.3)
    text(x+6.4,y+7,'x',3.5,anchor='middle',mono=True)
    text(x+10.7,y+11,'y',3.5,anchor='middle',mono=True)

def match_icon(x,y):
    rect(x,y,9,11,'white',1,.45)
    line([(x+2,y+2.5),(x+7,y+2.5)],.4)
    line([(x+2,y+4.5),(x+5,y+4.5)],.4)
    circle(x+7.5,y+8,3.2,'blue',lw=.6)
    line([(x+9.7,y+10.3),(x+12,y+12.5)],1.1)
    line([(x+6.1,y+8.1),(x+7.2,y+9),(x+9,y+6.8)],.55)

def dimension_badge(x,y,n,color):
    for dx,dy in [(1.4,-1.2),(.7,-.6),(0,0)]:rect(x+dx,y+dy,9,7.5,color,1,.35)
    text(x+4.5,y+5.5,str(n),5.4,True,'middle',mono=True)

# Remove the old Curve panel and its output arrow, preserving both upper panels.
for e in list(root):
    ident = e.get('id') or ''
    if ident.startswith('new_') and ident[4:].isdigit() and 6 <= int(ident[4:]) <= 118:
        root.remove(e)
panel = E.Element(f'{{{SVG}}}g', id='arithmetic44_panel')
idx = list(root).index(root.xpath('//*[@id="new_5"]')[0])
root.insert(idx+1,panel)

rect(14.58,230.5,189.46,176,'white',4.5,.65)
rect(14.58,230.68,189.46,14.7,'yellow',4.5,.65)
text(20.5,240.65,'3 Arithmetic response–evidence alignment',6.85,max_width=180)
text(109.2,252.2,'Three worlds, numeric answers and edited-cell coordinates',5.3,anchor='middle',max_width=177)

# Solid bypass carries the existing raw-response view and question cues directly.
line([(193,250),(199.1,250),(199.1,389)],.42)
arrow([(199.1,356),(196.6,356)],.42,head=1.2)
arrow([(199.1,389),(194.5,389)],.42,head=1.2)

# Exact operation family. The percent condition is stated below the candidate row.
rect(21,258,81,29,'blue',2.4,.5)
text(61.5,265,'One-step candidates',5.6,True,'middle')
table_icon(24,271)
formula(69,274,r'x_u^w+x_v^w,\quad x_u^w-x_v^w',6.1,max_width=58)
formula(69,282,r'x_u^w/x_v^w\quad [\times100\ \mathrm{if}\ \%]',5.65,max_width=58)
arrow([(103,272.5),(109,272.5)],.55)
rect(110.5,258,84,29,'yellow',2.4,.5)
text(152.5,265,'Match saved answer',5.6,True,'middle')
match_icon(114,271)
formula(158.5,274.5,r'd_w(r)=\frac{|r(E^w)-a^w|}{\tau_w}',7.0,max_width=63)
formula(157.6,283.5,r'\tau_w=\max(0.01,10^{-4}|a^w|)',5.9,max_width=65)

text(107.5,292,'Percent triplets also test 100(x/y − 1); at most 128 shared cells.',4.25,anchor='middle',max_width=175)
formula(107.5,300,r'M^w=\{r\in\mathcal{R}:d_w(r)\leq1\},\quad r=(o,u,v),\ u\ne v',7.1,max_width=174)
line([(107,302),(107,303.5)],.4)
line([(47.5,303.5),(165.5,303.5)],.4)
for cx in [47.5,106.5,165.5]:arrow([(cx,303.5),(cx,305.7)],.4,head=.9)

# Shared IDs retain the same operator and ordered cell coordinates across worlds.
for x,label,w,c in [(23,'Original','0','blue'),(82,'Positive','+','yellow'),(141,'Negative','-','pink')]:
    rect(x+1.25,305.9,49,17,c,2,.38)
    rect(x+.6,306.55,49,17,c,2,.38)
    rect(x,307.2,49,17,c,2,.48)
    text(x+24.5,313.5,label,4.8,True,'middle')
    formula(x+24.5,321,r'M^{'+w+'}',7.1)
line([(47.5,324.2),(47.5,327),(165.5,327),(165.5,324.2)],.45)
line([(106.5,324.2),(106.5,327)],.45)
arrow([(48,327),(48,331)],.45,head=1.4)
arrow([(111,327),(111,331)],.45,head=1.4)

# The three source-verified feature families: 24 + 16 + 4 = 44.
for x,w,c in [(20.5,57,'blue'),(81.5,59,'purple'),(144.5,52,'yellow')]:
    rect(x+1.0,331.6,w,43,c,2,.33)
    rect(x+.5,332.1,w,43,c,2,.33)
    rect(x,332.6,w,43,c,2,.5)
dimension_badge(22,333.8,24,'blue')
text(33.5,339.4,'World alignment',4.95,True,max_width=42)
text(49,347.5,'3 worlds × 8 summaries',4.6,True,'middle',max_width=52)
text(49,355.2,'log count · unique · edit',4.5,anchor='middle',max_width=51)
text(49,363,'row · column · year',4.3,anchor='middle',max_width=51)
text(49,370.8,'unit known · compatible',4.3,anchor='middle',max_width=51)

dimension_badge(83,333.8,16,'purple')
text(94.5,339.4,'Cross-world',5.0,True,max_width=42)
formula(111,349.5,r'I=M^0\cap M^+\cap M^-',6.4,max_width=54)
formula(111,360.5,r'J=\frac{|I|}{\max(1,|M^0\cup M^+\cup M^-|)}',6.3,max_width=53)
text(111,370.8,'switches · joint fit · context',4.0,anchor='middle',max_width=54)

dimension_badge(146,333.8,4,'yellow')
text(157.5,339.4,'Question cues',4.9,True,max_width=36)
# Small question/document icon: same simple vector vocabulary as the source.
rect(149,346,9,10,'white',1,.4)
text(153.5,353.3,'?',7.0,True,'middle')
text(175,351,'read · ratio',4.8,anchor='middle',max_width=31)
text(175,359,'change',4.8,anchor='middle')
text(175,367,'comparison',4.8,anchor='middle',max_width=33)

# Actual A44 column order: original8, positive8, negative8, joint16, question4.
for center in [49,111,170.5]:
    line([(center,375.6),(center,378)],.4)
line([(49,378),(170.5,378)],.4)
arrow([(84,378),(84,381)],.45,head=1.25)
text(79,385.4,'Arithmetic44 = 24 + 16 + 4',5.25,True,'middle',mono=True,max_width=116)
colors=['blue']*8+['yellow']*8+['pink']*8+['purple']*16+['cyan']*4
for i,c in enumerate(colors):
    x=22+i*2.53
    rect(x+.65,388.2,2.85,5.8,c,.35,.22)
    r=rect(x,389,2.85,5.8,c,.35,.25)
    r.set('data-a44-index',str(i))
    r.set('data-feature',schema['Arithmetic44']['feature_names'][i])

for dx,dy in [(1.4,-1.2),(.7,-.6),(0,0)]:rect(144+dx,382+dy,49,13.5,'yellow',1.8,.4)
text(168.5,387.4,'Raw16 + (h, t)',4.8,True,'middle',mono=True,max_width=45)
formula(168.5,393.8,r'R18',6.6)
text(109,403,'Numeric correspondence ≠ verified model reasoning',4.5,anchor='middle',max_width=180)

# Both representations feed fusion. No feature is derived from the label branch.
line([(83,395),(83,398),(194,398)],.5)
line([(168.5,395.5),(168.5,398)],.5)
arrow([(194,398),(194,414)],.55,head=1.8)

# The shared collector now explicitly includes the evidence worlds needed by A44.
label = root.xpath('//*[@id="new_5"]')[0]
label.clear()
label.set('id','new_5')
label.set('x','216.5'); label.set('y','154')
label.set('transform','rotate(-90 216.5 154)')
label.set('font-family','Arial'); label.set('font-size','5.2')
label.set('text-anchor','middle'); label.set('fill','black')
label.text='Three worlds + responses + edit coordinates'

# Mandatory downstream correction: 96 + 18 + 44 = 158, with unchanged detector.
risk=root.xpath('//*[@id="risk_panel"]')[0]
old_formula=risk.xpath('.//*[@id="new_122"]')[0]
position=list(risk).index(old_formula)
risk.remove(old_formula)
f=formula(109,440.8,r'\mathbf{z}=\operatorname{concat}(G96,R18,Arithmetic44)\in\mathbb{R}^{158}',7.0,parent=risk,max_width=176)
risk.remove(f); risk.insert(position,f)
f.set('id','raw44_fused_158')

metadata=E.SubElement(root,f'{{{SVG}}}metadata',id='raw44_method_provenance')
metadata.text=json.dumps({'source':'author supplied pecr_method_phenomenon_v4.svg',
    'method':'G96 + Raw16 + actual signed h and relative t + Arithmetic44',
    'features':{'G96':96,'Raw16':16,'edit':2,'Arithmetic44':44,'total':158},
    'schematic':True,'new_model_calls':0,'new_fits':0})

assert E.tostring(root.xpath('//*[@id="preserved_user_objects"]')[0]) == original_preserved
before=copy.deepcopy(original_risk)
after=copy.deepcopy(risk)
before.remove(before.xpath('.//*[@id="new_122"]')[0])
after.remove(after.xpath('.//*[@id="raw44_fused_158"]')[0])
# Insignificant indentation tails differ around the replacement.
def canonical(e):
    for n in e.iter():
        if n.tail and not n.tail.strip():n.tail=None
        if n.text and not n.text.strip():n.text=None
    return E.tostring(e)
assert canonical(before)==canonical(after)
ids=[e.get('id') for e in root.iter() if e.get('id')]
assert len(ids)==len(set(ids))
assert len(root.xpath('//*[@data-a44-index]'))==44
assert not root.xpath('//s:image',namespaces=NS)

OUT=ROOT/'figures'
name='pecr_method_raw44_v1'
p=OUT/(name+'.svg')
tree.write(str(p),encoding='utf-8',xml_declaration=True,pretty_print=True)
cairosvg.svg2png(url=str(p),write_to=str(OUT/(name+'.png')),output_width=1700)
cairosvg.svg2pdf(url=str(p),write_to=str(OUT/(name+'.pdf')))
subprocess.run(['pdftocairo','-svg',str(OUT/(name+'.pdf')),str(OUT/(name+'_outlined.svg'))],check=True)
detail=copy.deepcopy(root)
detail.set('viewBox','13 229 193 180')
detail.set('width','193pt');detail.set('height','180pt')
detail_path=OUT/'panel3_arithmetic44.svg'
E.ElementTree(detail).write(str(detail_path),encoding='utf-8',xml_declaration=True)
cairosvg.svg2png(url=str(detail_path),write_to=str(OUT/'panel3_arithmetic44.png'),output_width=1700)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'status':'PASS','source_svg_sha256':sha(SOURCE),'source_schema_sha256':sha(SCHEMA),
 'extractor_sha256':sha(EXTRACTOR),'upper_panels_native_objects_identical':True,
 'risk_panel_unchanged_except_fusion_formula':True,'arithmetic44_columns':44,
 'column_order':schema['world_order']+['joint16','question4'],
 'feature_dimensions':{'G96':96,'R18':18,'Arithmetic44':44,'fused':158},
 'vectors_only':True,'unique_element_ids':True,'observed_example_numbers_added':False,
 'new_model_calls':0,'new_fits':0,'gold_or_holdout_read':False,
 'size_pt':[218.27,507],'text_and_formula_bounds':text_bounds,
 'outputs':{q.name:sha(q) for q in OUT.iterdir() if q.is_file()}}
(ROOT/'VALIDATION.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
print(p)
