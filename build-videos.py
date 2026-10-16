#!/usr/bin/env python3
"""Nhanh Tay's home page videos: a strip of five tap-to-play cards under the hero, in every <lang>/index.html.
The videos (`../NhanhTay/Scripts/promo-videos.py`) are real takes of the game, so they show text: the owner chose
English + Vietnamese (2026-10-16): /vi/ plays video/<name>-vi.mp4, the other 33 pages video/<name>-en.mp4.
Each card's title reuses text the page already has: its tagline or the bold lead-in of a "What it is" bullet,
so nothing new is translated except "Close video" (video-close.json, the same 34 strings as squiggo-site).
Rewrites <!-- nhanhtay:videos --> ... <!-- /nhanhtay:videos --> (placed just after <!-- /family:shot -->).
Run `../_tools/site-family.py apply` + `lint` afterwards as usual; it leaves this block alone."""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).parent
CLOSE = json.loads((ROOT / "video-close.json").read_text())
# (video, card shape, title: "tagline", the index of the bullet in "What it is", or "language": the family sites'
# own word for Language, since the page's "Two quizzes" bullet predates the 34 languages the video shows)
VIDEOS = [("play", "tall", "tagline"), ("rules", "tall", 0), ("faster", "tall", 1), ("languages", "tall", "language"), ("ipad", "wide", 3)]
FAMILY_STRINGS = ROOT.parent / "_tools/site-family/strings"
A, B = "<!-- nhanhtay:videos -->", "<!-- /nhanhtay:videos -->"


def plain(s):
    s = re.sub(r"<[^>]+>", "", html.unescape(s)).strip()
    return re.sub(r"[\s,;:.。，、،;।]+$", "", s)


def titles(t):
    tagline = plain(re.search(r'<p class="tagline">(.*?)</p>', t, re.S).group(1))
    card = t[t.index('<section class="card">'):]
    card = card[:card.index("</section>")]
    leads = [(lambda s: s[:1].upper() + s[1:])(plain(m.group(1))) for li in re.findall(r"<li>(.*?)</li>", card, re.S) for m in [re.search(r"<strong>(.*?)</strong>", li, re.S)] if m]
    if len(leads) < 4: raise SystemExit(f"expected at least 4 bullets with a bold lead-in, found {len(leads)}")
    return tagline, leads


def block(t, lang, up):
    tagline, leads = titles(t)
    e = lambda s: html.escape(s, quote=True)
    v = "vi" if lang == "vi" else "en"
    cards = []
    for name, shape, ti in VIDEOS:
        if ti == "language":
            title = e(json.loads((FAMILY_STRINGS / f"{lang}.json").read_text())["language"])
        else:
            title = e(tagline if ti == "tagline" else leads[ti])
        src = f"{up}video/{name}-{v}"
        cards.append(f'<a class="nt-vcard {shape}" href="{src}.mp4" data-video data-title="{title}" data-poster="{src}.jpg" data-shape="{shape}">'
                     f'<img src="{src}.jpg" alt="" loading="lazy"><span class="play"></span><span class="cap">{title}</span></a>')
    return f'{A}\n<div class="nt-videos" data-close="{e(CLOSE[lang])}">{"".join(cards)}</div>\n<script src="{up}video.js" defer></script>\n{B}'


def build(lang):
    page = ROOT / ("index.html" if lang == "en" else f"{lang}/index.html")
    t = page.read_text()
    new = block(t, lang, "" if lang == "en" else "../")
    if A in t:
        t = t[:t.index(A)].rstrip("\n") + "\n\n" + t[t.index(B) + len(B):].lstrip("\n")
    # After the product shot: the modern look lifts the shot into the hero (.hero + .shot), so nothing goes between.
    i = t.index("<!-- /family:shot -->") + len("<!-- /family:shot -->")
    t = t[:i] + "\n" + new + t[i:]
    page.write_text(t)


if __name__ == "__main__":
    langs = sys.argv[1:] or ["en"] + sorted(p.parent.name for p in ROOT.glob("*/index.html") if p.parent.name in CLOSE)
    for l in langs: build(l)
    print(len(langs), "pages written")
