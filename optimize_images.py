from pathlib import Path
from PIL import Image
import re

ROOT = Path(__file__).parent / "dist"

def referenced_images():
    refs = set()
    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        for value in re.findall(r'(?:src|href)="([^"]+)"', text):
            if value.startswith(("http:", "https:", "#", "tel:", "mailto:")):
                continue
            path = (page.parent / value.split("#", 1)[0].split("?", 1)[0]).resolve()
            if path.suffix.lower() in {".webp", ".png", ".jpg", ".jpeg"} and path.exists():
                refs.add(path)
    return refs

refs = referenced_images()
before = {path: path.stat().st_size for path in refs}

# Re-encode displayed project photos without changing dimensions or aspect ratio.
# Lossless UI icons and logos stay untouched.
for path in refs:
    if path.suffix.lower() != ".webp" or path.name == "logo-header.webp":
        continue
    with Image.open(path) as image:
        image.save(path, "WEBP", quality=74, method=6)

after = {path: path.stat().st_size for path in refs}
for path in sorted(refs, key=lambda p: before[p] - after[p], reverse=True):
    print(f"{path.relative_to(ROOT)}\t{before[path]/1024:.1f} KB -> {after[path]/1024:.1f} KB")
print(f"TOTAL\t{sum(before.values())/1024:.1f} KB -> {sum(after.values())/1024:.1f} KB")

# Supply smaller sources to phones and tablets without changing the composition.
for page in ROOT.rglob("*.html"):
    text = page.read_text(encoding="utf-8")

    def add_responsive_source(match):
        tag = match.group(0)
        if "srcset=" in tag:
            return tag
        src_match = re.search(r'src="([^"]+\.webp)"', tag)
        if not src_match:
            return tag
        original = (page.parent / src_match.group(1)).resolve()
        if not original.exists():
            return tag
        with Image.open(original) as image:
            if image.width <= 800:
                return tag
            new_width = 720
            new_height = round(image.height * new_width / image.width)
            small = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            small_path = original.with_name(original.stem + "-720.webp")
            small.save(small_path, "WEBP", quality=72, method=6)
        small_ref = str(Path(src_match.group(1)).with_name(original.stem + "-720.webp")).replace("\\", "/")
        if "hero" in text[max(0, match.start()-120):match.start()].lower():
            sizes = "100vw"
        else:
            sizes = "(max-width:560px) 100vw, (max-width:980px) 50vw, 33vw"
        return tag[:-1] + f' srcset="{small_ref} 720w, {src_match.group(1)} {Image.open(original).width}w" sizes="{sizes}">'

    text = re.sub(r'<img\b[^>]*>', add_responsive_source, text)
    page.write_text(text, encoding="utf-8", newline="\n")
