from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import re

ROOT = Path(__file__).parent / "dist"
ASSETS = ROOT / "assets"
ORIGIN = "https://office-planet-interior.annakwaach.chatgpt.site"

# A compact logo for the 58px navigation/footer mark.
logo = Image.open(ASSETS / "office-planet-logo.png").convert("RGBA")
logo.thumbnail((160, 160), Image.Resampling.LANCZOS)
logo.save(ASSETS / "logo-header.webp", "WEBP", quality=82, method=6)

# A landscape social card for WhatsApp, Facebook, LinkedIn and X previews.
photo = Image.open(ASSETS / "client-work" / "home-restaurant-bar-counter.webp").convert("RGB")
target = (1200, 630)
scale = max(target[0] / photo.width, target[1] / photo.height)
photo = photo.resize((round(photo.width * scale), round(photo.height * scale)), Image.Resampling.LANCZOS)
left = (photo.width - target[0]) // 2
top = (photo.height - target[1]) // 2
card = photo.crop((left, top, left + target[0], top + target[1])).convert("RGBA")
overlay = Image.new("RGBA", target, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)
draw.rectangle((0, 0, 520, 630), fill=(13, 13, 14, 218))
draw.rectangle((0, 0, 14, 630), fill=(204, 145, 55, 255))
card = Image.alpha_composite(card, overlay)

mark = Image.open(ASSETS / "office-planet-logo.png").convert("RGBA")
mark.thumbnail((230, 230), Image.Resampling.LANCZOS)
card.alpha_composite(mark, (140, 40))
draw = ImageDraw.Draw(card)
font_paths = [
    Path("C:/Windows/Fonts/georgia.ttf"),
    Path("C:/Windows/Fonts/arial.ttf"),
]
font_path = next((p for p in font_paths if p.exists()), None)
title_font = ImageFont.truetype(str(font_path), 54) if font_path else ImageFont.load_default()
small_font = ImageFont.truetype(str(font_path), 25) if font_path else ImageFont.load_default()
draw.text((62, 330), "OFFICE PLANET", font=title_font, fill=(255, 255, 255, 255))
draw.text((62, 394), "INTERIOR", font=title_font, fill=(218, 164, 73, 255))
draw.text((65, 482), "Interior design & fit-outs · Kenya", font=small_font, fill=(242, 237, 228, 255))
card.convert("RGB").save(ASSETS / "social-share.jpg", "JPEG", quality=85, optimize=True, progressive=True)

for html_path in ROOT.rglob("*.html"):
    text = html_path.read_text(encoding="utf-8")
    nested = html_path.parent != ROOT
    prefix = "../" if nested else ""

    # Remove old/duplicate favicon declarations and install compact standards-based icons.
    text = re.sub(r'<link rel="icon"[^>]*>', '', text)
    text = re.sub(r'<link rel="apple-touch-icon"[^>]*>', '', text)
    icons = (
        f'<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml">'
        f'<link rel="icon" href="{prefix}assets/favicon-32.png" sizes="32x32" type="image/png">'
        f'<link rel="apple-touch-icon" href="{prefix}assets/apple-touch-icon.png">'
    )
    text = text.replace('<meta name="viewport" content="width=device-width,initial-scale=1">', '<meta name="viewport" content="width=device-width,initial-scale=1">' + icons)
    text = text.replace('<meta name="viewport" content="width=device-width, initial-scale=1">', '<meta name="viewport" content="width=device-width, initial-scale=1">' + icons)

    # Correct stale brand references and use a purpose-built landscape social preview.
    text = text.replace("Elegants Fittings", "Office Planet Interior")
    text = text.replace("Explore the five specialist interior design and fit-out services", "Explore the six specialist interior design and fit-out services")
    text = re.sub(r'<meta property="og:image" content="[^"]+">', f'<meta property="og:image" content="{ORIGIN}/assets/social-share.jpg">', text)
    text = re.sub(r'<meta property="og:image:secure_url" content="[^"]+">', f'<meta property="og:image:secure_url" content="{ORIGIN}/assets/social-share.jpg">', text)
    text = re.sub(r'<meta property="og:image:type" content="[^"]+">', '<meta property="og:image:type" content="image/jpeg">', text)
    text = re.sub(r'<meta property="og:image:width" content="[^"]+">', '<meta property="og:image:width" content="1200">', text)
    text = re.sub(r'<meta property="og:image:height" content="[^"]+">', '<meta property="og:image:height" content="630">', text)
    text = re.sub(r'<meta name="twitter:card" content="[^"]+">', '<meta name="twitter:card" content="summary_large_image">', text)
    text = re.sub(r'<meta name="twitter:image" content="[^"]+">', f'<meta name="twitter:image" content="{ORIGIN}/assets/social-share.jpg">', text)

    # Avoid loading the 1.3MB master artwork for every tiny brand mark.
    text = text.replace(f'src="{prefix}assets/office-planet-logo.png" width="58" height="58"', f'src="{prefix}assets/logo-header.webp" width="58" height="58"')

    # Reserve image space to prevent layout shifts; prioritize the service hero image.
    def add_dimensions(match):
        tag = match.group(0)
        if ' width=' in tag and ' height=' in tag:
            return tag
        src_match = re.search(r'src="([^"]+)"', tag)
        if not src_match or src_match.group(1).startswith(('http:', 'https:', 'data:')):
            return tag
        image_path = (html_path.parent / src_match.group(1)).resolve()
        try:
            with Image.open(image_path) as im:
                width, height = im.size
            tag = tag[:-1] + f' width="{width}" height="{height}">'
            if 'single-service-hero' in text[max(0, match.start()-80):match.start()] and 'fetchpriority=' not in tag:
                tag = tag[:-1] + ' fetchpriority="high">'
        except Exception:
            pass
        return tag
    text = re.sub(r'<img\b[^>]*>', add_dimensions, text)

    # Keep only the verified social contact and remove the render-blocking icon font.
    text = re.sub(r'<link rel="preconnect" href="https://cdnjs\.cloudflare\.com" crossorigin>', '', text)
    text = re.sub(r'<link rel="stylesheet" href="https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/[^\"]+">', '', text)
    text = re.sub(
        r'<div class="footer-social" aria-label="Social media">.*?</div>',
        '<div class="footer-social"><a class="footer-whatsapp" href="https://wa.me/254726138627" target="_blank" rel="noopener noreferrer">WhatsApp ↗</a></div>',
        text,
        flags=re.S,
    )

    html_path.write_text(text, encoding="utf-8", newline="\n")

# Keep the manifest fast and point to the existing optimized app icons.
(ROOT / "site.webmanifest").write_text('''{
  "name": "Office Planet Interior",
  "short_name": "Office Planet",
  "icons": [
    {"src": "assets/icon-192.png", "sizes": "192x192", "type": "image/png"},
    {"src": "assets/icon-512.png", "sizes": "512x512", "type": "image/png"}
  ],
  "theme_color": "#78836f",
  "background_color": "#f7f3ec",
  "display": "standalone"
}
''', encoding="utf-8")
