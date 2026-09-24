from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
from PIL import Image
from collections import Counter
import json

ROOT = Path(__file__).parent / "dist"

class Parser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs=[]; self.ids=[]; self.images=[]; self.h1=0; self.title=0; self.descriptions=0
    def handle_starttag(self, tag, attrs):
        a=dict(attrs)
        if "id" in a: self.ids.append(a["id"])
        if tag=="h1": self.h1+=1
        if tag=="title": self.title+=1
        if tag=="meta" and a.get("name")=="description": self.descriptions+=1
        if tag in ("a","link","script","img"):
            key="href" if tag in ("a","link") else "src"
            if key in a: self.refs.append((tag,a[key]))
        if tag=="img": self.images.append(a)

issues=[]
for page in ROOT.rglob("*.html"):
    p=Parser(); p.feed(page.read_text(encoding="utf-8"))
    if p.h1 != 1: issues.append(f"{page.relative_to(ROOT)}: expected one h1, found {p.h1}")
    if p.descriptions != 1: issues.append(f"{page.relative_to(ROOT)}: expected one description, found {p.descriptions}")
    dup=[k for k,v in Counter(p.ids).items() if v>1]
    if dup: issues.append(f"{page.relative_to(ROOT)}: duplicate ids {dup}")
    for tag,ref in p.refs:
        if not ref or ref.startswith(("http://","https://","mailto:","tel:","#","data:")): continue
        local=ref.split("#",1)[0].split("?",1)[0]
        target=(page.parent/local).resolve()
        if local and not target.exists(): issues.append(f"{page.relative_to(ROOT)}: missing {tag} target {ref}")
    for a in p.images:
        src=a.get("src","")
        target=(page.parent/src).resolve()
        if not a.get("alt"): issues.append(f"{page.relative_to(ROOT)}: image missing alt {src}")
        if "width" not in a or "height" not in a: issues.append(f"{page.relative_to(ROOT)}: image missing dimensions {src}")

print(json.dumps({"pages":len(list(ROOT.rglob('*.html'))),"issues":issues},indent=2))
