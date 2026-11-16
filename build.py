#!/usr/bin/env python3
"""Build the Gaia Lab website from the files in data/.

  python3 build.py            live site in this folder (thegaialab.com/team/ etc.), images from media/
  python3 build.py --preview  flat copy in preview/ with CSS and JS inlined (Claude artifact preview)
  python3 build.py --pane     flat copy in pane/ that loads images from thegaialab.com (browser check)

Content lives in data/*.json. Images and PDFs live in media/YYYY/MM/<file>,
mirroring the old WordPress upload paths.
"""
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).parent
MODE = "pane" if "--pane" in sys.argv else "preview" if "--preview" in sys.argv else "live"
FLAT = MODE != "live"
OUT = ROOT / MODE if FLAT else ROOT

people = json.loads((ROOT / "data/people.json").read_text())
pubs = json.loads((ROOT / "data/publications.json").read_text())
themes = json.loads((ROOT / "data/themes.json").read_text())
misc = json.loads((ROOT / "data/misc.json").read_text())


# Every new entry must have the same structure as the existing entries of its kind.
# The build stops if an entry has a field that its siblings do not use or lacks a required field.
TEAM_GROUPS = {"Postdoctoral researchers": "Postdoctoral Associates / Fellows",
               "Graduate students": "Graduate Students",
               "Undergraduate researchers": "Undergraduate Researchers"}
MEMBER_REQUIRED = {"name", "since", "photo", "bio"}
MEMBER_ALLOWED = {"name", "since", "photo", "photo2", "website", "bio"}
ALUM_REQUIRED = {"name", "role", "photo"}
ALUM_ALLOWED = {"name", "role", "project", "photo", "photo2", "is_bio", "now"}


def check_people():
    bad = []
    for g in people["groups"]:
        if g["name"] not in TEAM_GROUPS:
            bad.append(f'unknown team group "{g["name"]}"')
        for m in g["members"]:
            k = set(m)
            if MEMBER_REQUIRED - k or k - MEMBER_ALLOWED:
                bad.append(f'{m.get("name")}: missing {sorted(MEMBER_REQUIRED - k)}, unexpected {sorted(k - MEMBER_ALLOWED)}')
            if not m.get("bio", "").strip():
                bad.append(f'{m.get("name")}: empty bio')
    for a in people["alumni"]:
        k = set(a)
        if ALUM_REQUIRED - k or k - ALUM_ALLOWED:
            bad.append(f'alumni {a.get("name")}: missing {sorted(ALUM_REQUIRED - k)}, unexpected {sorted(k - ALUM_ALLOWED)}')
    if bad:
        raise SystemExit("people.json does not match the existing entry format:\n  " + "\n  ".join(bad))


check_people()

NAV = [("", "Home"), ("team", "Team"),
       ("research", "Research", [("themes", "Themes"), ("publications", "Publications"), ("resources", "Data & code")]),
       ("outreach", "Engagement", [("outreach#teaching", "Teaching"), ("outreach#talks", "Outreach"), ("outreach#media", "In the media")]),
       ("fieldwork", "Gallery")]
FONTS = "https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,500&family=Raleway:ital,wght@0,400;0,700;1,400&display=swap"
EMAIL = "gaias@mit.edu"
e = html.escape
CUR = {"depth": 0}
U = "https://thegaialab.files.wordpress.com/"  # short prefix for image paths below


def ver(path):
    """Short content hash so browsers fetch the new file after every change."""
    import hashlib
    return hashlib.md5((ROOT / path).read_bytes()).hexdigest()[:8]


def rel(path):
    return ("../" * CUR["depth"]) + path


def link(slug):
    if FLAT:
        return f"{slug or 'index'}.html"
    return rel(f"{slug}/" if slug else "") or "./"


def media(url):
    if not url:
        return ""
    if url.startswith("assets/"):
        return rel(url)
    u = urlparse(url)
    if not ("wordpress.com" in u.netloc or "thegaialab.com" in u.netloc):
        return url
    m = re.search(r"/(\d{4}/\d{2}/[^/?#]+)$", u.path)
    if not m:
        return url
    # Until the WordPress images are copied into media/, load any missing file from WordPress.
    if MODE == "pane" or not (ROOT / "media" / m.group(1)).exists():
        big = "" if m.group(1).endswith((".gif", ".pdf")) else "?w=1600"
        return f"https://thegaialab.com/wp-content/uploads/{m.group(1)}{big}"
    return rel(f"media/{m.group(1)}")


def img(url, alt="", eager=False):
    load = "" if eager else ' loading="lazy" decoding="async"'
    return f'<img src="{e(media(url))}" alt="{e(alt)}"{load}>'


def pic(url, alt="", cls="", style="", drift=0, eager=False, grow=False):
    d = f' data-drift="{drift}"' if drift else ""
    d += ' data-grow' if grow else ""
    s = f' style="{style}"' if style else ""
    return f'<div class="pic {cls}"{s}{d}>{img(url, alt, eager)}</div>'


def window(photo, inner="", h=None, cls="", tag="", pos=None):
    # url() inside a CSS variable resolves against assets/style.css, so local paths are written relative to assets/.
    u = media(photo) if photo else ""
    if u and not u.startswith(("http:", "https:", "data:")):
        u = "../" + u[len("../" * CUR["depth"]):]
    style = (f"--img:url('{u}');" if photo else "") + (f"--h:{h};" if h else "") + (f"--bp:{pos};" if pos else "")
    t = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<section class="window {cls}" style="{style}"><div class="in">{inner}</div>{t}</section>'


RIVER_N = [0]


def _smooth(pts):
    """Catmull-Rom points to a cubic Bezier path."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[max(i - 1, 0)]; p1 = pts[i]; p2 = pts[i + 1]; p3 = pts[min(i + 2, len(pts) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


def dots(words=True):
    """A divider drawn after the lab's river GIF: three meandering headwater threads join into one
    looping channel, and pale rounded chevrons travel downstream along every thread."""
    import math, random
    RIVER_N[0] += 1
    n = RIVER_N[0]
    rnd = random.Random(1000 + n)
    H = 100
    # main channel: sine-generated curve (Langbein), which gives real meander loops
    ds = 4
    pts, x, y, th, k = [], 0.0, 0.0, rnd.uniform(-0.3, 0.3), rnd.gauss(0, 0.03)
    while x < 1300:
        # curvature wanders at random; weak pulls keep the channel heading downstream and inside the strip
        k = 0.94 * k + rnd.gauss(0, 0.012)
        th += k - 0.035 * th - 0.0009 * y
        x += ds * math.cos(th); y += ds * math.sin(th)
        pts.append((x, y))
    ys = [p[1] for p in pts]
    mid = (max(ys) + min(ys)) / 2
    xs = [p[0] for p in pts]
    sc = min(1.0, 76 / max(1, max(ys) - min(ys)))
    main = [(-20 + px, H / 2 + (py - mid) * sc) for px, py in pts][::4]
    tribs = []
    chev = '<path d="M-1 -6.5 Q9 0 -1 6.5 L-10 6.5 Q0 0 -10 -6.5 Z"/>'
    chev_s = '<path d="M-1 -3.5 Q5 0 -1 3.5 L-6 3.5 Q0 0 -6 -3.5 Z"/>'
    def movers(pid, shape, count, dur):
        return "".join(f'<g class="chev"><use href="#{shape}"/><animateMotion dur="{dur}s" begin="-{dur * i / count:.2f}s" repeatCount="indefinite" rotate="auto"><mpath href="#{pid}"/></animateMotion></g>'
                       for i in range(count))
    defs, layers, moves = [chev.replace('<path ', f'<path id="rv{n}c" '), chev_s.replace('<path ', f'<path id="rv{n}cs" ')], [], []
    for i, tp in enumerate(tribs):
        pid = f"rv{n}t{i}"
        defs.append(f'<path id="{pid}" d="{_smooth(tp)}" pathLength="1"/>')
        layers.append(f'<use class="bank thin" href="#{pid}"/><use class="water thin" href="#{pid}"/>')
        moves.append(movers(pid, f"rv{n}cs", 2, 4))
    pid = f"rv{n}m"
    defs.append(f'<path id="{pid}" d="{_smooth(main)}" pathLength="1"/>')
    layers.append(f'<use class="water" href="#{pid}"/>')
    moves.append(movers(pid, f"rv{n}c", 9, 11))
    return (f'<div class="river" data-river aria-hidden="true"><svg viewBox="0 0 1200 {H}" preserveAspectRatio="xMidYMid meet">'
            f'<defs>{"".join(defs)}</defs>{"".join(layers)}<g class="chevs">{"".join(moves)}</g></svg></div>')


def btn(label, href, cls=""):
    return f'<a class="btn {cls}" href="{href}">{e(label)} <span class="arr" aria-hidden="true">→</span></a>'


def embed(src, thumb, title):
    play = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M7 4v16l13-8z"/></svg>'
    return (f'<div class="embed"><button type="button" class="facade" data-src="{e(src)}" data-title="{e(title)}" aria-label="Play {e(title)}">'
            f'<img src="{e(thumb)}" alt="" loading="lazy" onload="if(this.naturalWidth<=120&&this.src.indexOf(\'maxres\')>0)this.src=this.src.replace(\'maxresdefault\',\'hqdefault\')"><span>{play}</span></button></div>')


def yt(vid, start=0):
    st = f"&start={start}" if start else ""
    return f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&rel=0{st}", f"https://i.ytimg.com/vi/{vid}/maxresdefault.jpg"


def md(s):
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", s)
    return s


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


# Preview site must stay hidden from search engines. Set to False only when Gaia approves the domain switch.
NOINDEX = False

# One height for every page banner (Home keeps its taller welcome hero).
BANNER_H = "60vh"

LAB_LINKEDIN = "https://www.linkedin.com/company/136993897/"


ICONS = {
    "LinkedIn": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9h4v12H3zM9 9h3.8v1.7h.05c.53-1 1.84-2.05 3.8-2.05C20.6 8.65 21 11.2 21 14.5V21h-4v-5.8c0-1.4-.03-3.2-1.95-3.2-1.95 0-2.25 1.5-2.25 3.1V21H9z"/></svg>',
    "Google Scholar": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 3 1 9.5l4 2.36V17c0 1.66 3.13 3 7 3s7-1.34 7-3v-5.14l2-1.18V16h2V9.5zm5 13.9c-.4.56-2.2 1.6-5 1.6s-4.6-1.04-5-1.6v-3.86l5 2.95 5-2.95z"/></svg>',
    "GitHub": '<svg viewBox="0 0 24 24"><path fill="currentColor" d="M12 2a10 10 0 0 0-3.16 19.49c.5.09.68-.22.68-.48v-1.7c-2.78.6-3.37-1.34-3.37-1.34-.45-1.15-1.11-1.46-1.11-1.46-.91-.62.07-.6.07-.6 1 .07 1.53 1.03 1.53 1.03.9 1.52 2.34 1.08 2.91.83.09-.65.35-1.08.63-1.33-2.22-.25-4.55-1.11-4.55-4.94 0-1.09.39-1.98 1.03-2.68-.1-.25-.45-1.27.1-2.65 0 0 .84-.27 2.75 1.02a9.6 9.6 0 0 1 5 0c1.91-1.29 2.75-1.02 2.75-1.02.55 1.38.2 2.4.1 2.65.64.7 1.03 1.59 1.03 2.68 0 3.84-2.34 4.69-4.57 4.93.36.31.68.92.68 1.85v2.74c0 .27.18.58.69.48A10 10 0 0 0 12 2z"/></svg>',
}
PAGES = {}


def page(slug, title, body, description):
    CUR["depth"] = 0 if (FLAT or not slug) else 1
    items = []
    for it in NAV:
        if len(it) == 3:
            subs = it[2]
            on = any(sl.split("#")[0] == slug for sl, _ in subs)
            href = lambda sl: link(sl.split("#")[0]) + ("#" + sl.split("#")[1] if "#" in sl else "")
            inner = "".join(f'<a href="{href(sl)}"{" aria-current=\"page\"" if sl == slug else ""}>{e(lb)}</a>' for sl, lb in subs)
            items.append(f'<div class="drop{" on" if on else ""}"><a href="{link(subs[0][0].split("#")[0])}" class="drop-top"{" aria-current=\"true\"" if on else ""}>{e(it[1])} <span aria-hidden="true">▾</span></a><div class="drop-menu">{inner}</div></div>')
        else:
            sl, lb = it
            items.append(f'<a href="{link(sl)}"{" aria-current=\"page\"" if sl == slug or (sl and slug.startswith(sl + "-")) else ""}>{e(lb)}</a>')
    items.append(f'<a href="{link("contact-cv")}" class="nav-contact"{" aria-current=\"page\"" if slug == "contact-cv" else ""}>Contact</a>')
    nav = "".join(items)
    icons = "".join(f'<a href="{u}" aria-label="{n}">{ICONS[n]}</a>' for n, u in [
        ("LinkedIn", "https://www.linkedin.com/in/g-stucky/"),
        ("Google Scholar", "https://scholar.google.com/citations?user=uJNld2AAAAAJ&amp;hl=en"),
        ("GitHub", "https://github.com/gaiastucky")])
    full_title = "The Gaia Lab" if not slug else f"{title} | The Gaia Lab"
    geo = ('<script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>'
           '<script src="https://cdn.jsdelivr.net/npm/topojson-client@3.1.0/dist/topojson-client.min.js"></script>') if slug in ("", "fieldwork") else ""
    if FLAT:
        css = f"<style>{(ROOT / 'assets/style.css').read_text()}</style>"
        js = f"<script>{(ROOT / 'assets/site.js').read_text()}</script>"
    else:
        css = f'<link rel="stylesheet" href="{rel("assets/style.css")}?v={ver("assets/style.css")}">'
        js = f'<script src="{rel("assets/site.js")}?v={ver("assets/site.js")}" defer></script>'
    head = (f"<title>{e(full_title)}</title>\n<meta name=\"description\" content=\"{e(description)}\">\n"
            '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link rel="stylesheet" href="{FONTS}">\n{css}\n')
    content = f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="head-in">
<a class="mark" href="{link('')}"><span class="mark-badge"><img class="mark-logo" src="{rel('assets/logo.webp')}" alt="" width="900" height="856"></span><span class="mark-txt"><b>The Gaia Lab</b><span>Exploring landscapes across the Solar System</span></span></a>
<button class="menu-btn" id="menu-btn" type="button" aria-expanded="false" aria-controls="head-right">Menu</button>
<div class="head-right" id="head-right"><nav class="nav" aria-label="Main">{nav}</nav><div class="icons">{icons}</div></div>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="foot-in">
<div><b>The Gaia Lab</b><br>Department of Earth, Atmospheric and Planetary Sciences<br>Massachusetts Institute of Technology</div>
<div>Room 54-319, Green Building<br>Cambridge, MA 02139<br><a href="{link('contact-cv')}">Get in touch</a></div>
</div></footer>
{geo}{js}"""
    if MODE == "preview" and not slug:
        doc = head + content
    else:
        doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
               + ('<meta name="robots" content="noindex, nofollow">\n' if NOINDEX else '')
               + f"{head}</head>\n<body>\n{content}\n</body>\n</html>\n")
    path = OUT / f"{slug or 'index'}.html" if FLAT else (OUT / slug / "index.html" if slug else OUT / "index.html")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc)
    PAGES[slug or "index"] = doc


def set_depth(slug):
    CUR["depth"] = 0 if (FLAT or not slug) else 1


# ======================================================================= Home
BLIPS = [
    ("24", "%", "of the volume of incised valleys on early Mars was carved by lake breach floods.", "Goudge et al., Nature (2021)", "https://doi.org/10.1038/s41586-021-03860-1"),
    ("100–10⁴", "yr", "is how long individual runoff episodes lasted on early Mars, repeated many times.", "Stucky de Quay et al., GRL (2021)", "https://doi.org/10.1029/2021GL093523"),
    ("4–159", "m", "of basin-averaged precipitation was needed to fill almost 100 Martian paleolakes.", "Stucky de Quay et al., Geology (2020)", "https://doi.org/10.1130/G47886.1"),
    ("½", "million", "drainage basins on Earth are mapped in our global dataset of basin shapes.", "He et al., ESSD (2024)", "https://doi.org/10.5194/essd-16-1151-2024"),
]


def slide_names(start):
    names = [t["name"] for t in themes]
    names = names[start:] + names[:start]
    return "".join(f"<span>{e(n)}</span><i aria-hidden=\"true\"></i>" for n in names * 2)


def strip_photos():
    az, ic = misc["fieldwork"][0]["photos"], misc["fieldwork"][1]["photos"]
    picks = [ic[0], az[0], ic[3], az[5], ic[8], az[9], ic[12], az[13], ic[15], az[2]]
    out = []
    for k, u in enumerate(picks):
        place = "Northeast Iceland, 2017" if u in ic else "Azores, 2020"
        out.append(f'<figure class="strip-ph s{k % 3}">{img(u, place, eager=True)}<figcaption>{place}</figcaption></figure>')
    return "".join(out)


def teaser(photo, title, text, href, label="Read more", i=0):
    return (f'<li class="teaser" data-reveal="{i}"><a href="{href}" class="teaser-pic" tabindex="-1" aria-hidden="true">{pic(photo, "", "round", grow=True)}</a>'
            f'<h3>{e(title)}</h3><p>{text}</p>{btn(label, href, "line")}</li>')


GLOBE_PLACES = [
    {"id": "northeast-iceland", "name": "Northeast Iceland", "year": 2017, "lat": 65.8, "lon": -16.4, "photo": "https://thegaialab.files.wordpress.com/2022/01/img_0571.jpg"},
    {"id": "azores", "name": "Azores", "year": 2020, "lat": 38.5, "lon": -28.4, "photo": "https://thegaialab.files.wordpress.com/2022/01/img_6319-1.jpg"},
]


FIELD_SITES = [  # every place we have worked; shown as unlabelled pins that open that trip's gallery
    (65.85, -16.40, "Northeast Iceland"),   # Jökulsá á Fjöllum canyon
    (38.39, -28.26, "Azores"),              # Lajes do Pico
    (38.60, -27.94, "Azores"),              # Fajã da Caldeira de Santo Cristo, São Jorge
    (36.97, -25.10, "Azores"),              # Santa Maria
    (29.05, -13.65, "Lanzarote"),           # Lanzarote, Canary Islands
    (16.60, -24.25, "São Nicolau"),         # São Nicolau, Cape Verde
    (14.95, -24.38, "Fogo"),                # Fogo, Cape Verde
    (19.98, 76.51, "Lonar"),                # Lonar crater, Maharashtra, India
]


TRIP_TITLE = {"Lonar": "Lonar, India"}  # display names where the place alone is not enough


def trip_title(place):
    return TRIP_TITLE.get(place, place)


def trip_slug(place):
    import unicodedata
    return "fieldwork-" + slugify(unicodedata.normalize("NFKD", place).encode("ascii", "ignore").decode())


def globe_block(big=False):
    pts = json.dumps([{"lat": a, "lon": b, "href": link(trip_slug(p)), "name": trip_title(p)} for a, b, p in FIELD_SITES]).replace('"', "&quot;")
    if big:  # on the gallery page the pins are the only links
        return (f'<div class="globe-wrap big" role="img" aria-label="A turning globe with pins at our field sites. Click a pin to open its photos">'
                f'<canvas id="globe" width="460" height="460" data-places="{pts}"></canvas></div>')
    return (f'<a class="globe-wrap" href="{link("fieldwork")}" aria-label="A turning globe with pins at our field sites. Open the gallery">'
            f'<canvas id="globe" width="460" height="460" data-places="{pts}"></canvas></a>')


def main_themes():
    out = []
    for i, t in enumerate([t for t in themes if t.get("main")]):
        out.append(f'<li data-reveal="{i}"><a href="{link("themes")}#{t["id"]}">{pic(t["img"], t["name"], "round", grow=True)}'
                   f'<h3>{e(t["name"])}</h3><p>{md(t["q"][0])}</p></a></li>')
    return "".join(out)


def story(kicker, title, text, href, label, art, flip=False, i=0):
    return (f'<section class="story{" alt" if flip else ""}"><div class="story-art" data-reveal>{art}</div>'
            f'<div class="story-text" data-reveal="1"><h2 class="h2">{e(title)}</h2>'
            f'<p>{text}</p><div class="actions">{btn(label, href)}</div></div></section>')


def art(main, sats=()):
    out = f'<a class="art-main">{pic(main, "", "round", grow=True)}</a>'
    for j, sat in enumerate(sats):
        out += pic(sat, "", f"round sat sat{j}", drift=(-40 if j else 50))
    return out


def home():
    set_depth("")
    mt = [t for t in themes if t.get("main")]
    stories = "".join([
        story("Research", "Probing the surface",
              "Check out the <strong>research topics</strong> we are curious about, and what questions keep us up at night.",
              link("themes"), "Explore themes", art(mt[0]["img"], [mt[1]["img"], mt[2]["img"]])),
        story("Publications", "Discover published work",
              "From the laptop screen to the field, learn about our most recent contributions.",
              link("publications"), "Read more",
              art("https://thegaialab.files.wordpress.com/2022/09/perspective.png", ["https://thegaialab.files.wordpress.com/2021/11/screen-shot-2021-11-14-at-11.01.49-pm.png", "https://thegaialab.files.wordpress.com/2021/11/screen-shot-2021-11-14-at-11.32.15-pm.png"]), flip=True),
        story("Fieldwork", "Excited about the great outdoors?",
              "So are we! We travel all over the globe to find interesting and unique places to answer questions about how and why landscapes look the way they do. Click the globe to see where we have been.",
              link("fieldwork"), "Follow our journeys", globe_block()),
        story("Team", "Learn about us",
              "Find out who is in our team so far. And whether there is a place for you!",
              link("team"), "Yes please", art(people["group_photo"], [people["mascot"]["photo"]]), flip=True),
    ])
    hero = ('<h1 data-hero><span class="hello" aria-label="Hello there!">' + ''.join(f'<span style="--i:{k}" aria-hidden="true">{"&nbsp;" if ch == " " else ch}</span>' for k, ch in enumerate('Hello there!')) + '</span> Welcome to the Gaia Lab.</h1>'
            '<p class="sub" data-hero>We study the driving forces behind the formation, evolution, and decay of Solar System surfaces, '
            'and the coupled interactions between climate, erosion, and tectonics recorded in landscapes. <em>Find out more below!</em></p>')
    li_posts = "".join(f'<iframe src="https://www.linkedin.com/embed/feed/update/{u}" title="LinkedIn post by The Gaia Lab" loading="lazy" allowfullscreen></iframe>' for u in misc.get("linkedin_posts", []))
    body = f"""{window(misc['covers']['home'], hero, h='78vh', cls='hero', tag='Jökulsá á Fjöllum canyon, Iceland, 2017')}
<section class="logo-stage" aria-label="The Gaia Lab logo"><div class="logo-anim" data-reveal>
<img src="{rel('assets/logo.webp')}" alt="The Gaia Lab logo: a planet of layered mountains and a river, circled by an orbit with a satellite">
<div class="logo-sky" aria-hidden="true"><div class="band stars"><i class="ss s1"></i><i class="ss s2"></i><i class="ss s3"></i></div><div class="band clouds"><i class="cl c1"></i><i class="cl c2"></i><i class="cl c3"></i></div></div>

</div></section>

<section class="story intro">
<div class="story-text" data-reveal><h2 class="h2">What we do, and why</h2>
<p>Have you ever looked at a landscape and thought, “<em>Wow, that looks cool. How did that happen</em>”? Then welcome to the club (if not, that's okay). From your backyard to faraway moons, <strong>river systems</strong> dictate how surfaces evolve over geological time.</p>
<div class="actions"><button class="sound" id="sound" type="button"><i></i>Play some sweet river sounds</button></div>
<div class="sound-frame" id="sound-frame"></div></div>
<div class="story-art gif" data-reveal="1"><img src="{media(U + '2022/01/water_gif-3.gif')}" alt="Animated block diagram of a river cutting through a landscape" loading="lazy"></div>
</section>

{dots()}

{stories}

{dots()}

<section class="section linkedin" data-reveal><a class="li-badge" href="{LAB_LINKEDIN}" aria-hidden="true" tabindex="-1">{ICONS["LinkedIn"]}</a>
<h2 class="h2">Follow us on LinkedIn</h2>
<div class="li-posts">{li_posts}</div>
<div class="actions">{btn("Follow us", LAB_LINKEDIN)}</div></section>"""
    page("", "Home", body, "The Gaia Lab at MIT: exploring landscapes across the Solar System.")


# ======================================================================= Team
def person(m, extra="", i=0):
    since = f'<p class="since">{e(m["since"])}{"" if "–" in m["since"] else "–"}</p>' if m.get("since") else (f'<p class="since">{e(m["role"])}</p>' if m.get("role") and m.get("is_pi") else "")
    site = f'<div class="actions">{btn("Website", m["website"], "line")}</div>' if m.get("website") else ""
    anchor = "io" if m["name"].startswith("Io ") else slugify(m["name"])
    left = pic(m["photo"], m["name"], "round")
    right = pic(m["photo2"], "", "round") if m.get("photo2") else "<div></div>"
    return f"""<article class="person" id="{anchor}" data-split>
{left}
<div><h3>{e(m['name'])}</h3>{since}<p class="bio drop">{m['bio']}</p>{site}{extra}</div>
{right}
</article>"""


def team():
    set_depth("team")
    pi = dict(people["pi"], bio=" ".join(people["pi"]["bio"]), is_pi=True, role="Principal Investigator")
    pi_extra = f'<div class="actions">{btn("Get in touch", link("contact-cv"))}</div>'
    order = list(TEAM_GROUPS)
    groups = "".join(
        f'<section class="section"><div class="group-head" data-reveal><h2 class="h2">{e(TEAM_GROUPS[g["name"]])}</h2></div><div class="stack-people">{"".join(person(m) for m in g["members"])}</div></section>'
        for g in sorted(people["groups"], key=lambda g: order.index(g["name"])) if g["members"])
    def tier(a):
        r = a["role"].lower()
        return 2 if "visiting" in r else 0 if "postdoc" in r else 1 if ("phd" in r or "master" in r or "grad" in r and "undergrad" not in r) else 2 if "visiting" in r else 3
    def year(a):
        ys = re.findall(r"20\d\d", a["role"])
        return -int(ys[-1]) if ys else 0
    def alum_pic(a, k):
        if not a.get("photo2"):
            return pic(a["photo"], a["name"], "round")
        return (f'<div class="alum-flip" style="--d:{k}">{pic(a["photo"], a["name"], "round af-front")}'
                f'{pic(a["photo2"], "", "round af-back")}</div>')
    tiers = [("Postdocs", 0), ("Graduate students", 1), ("Visiting members", 2), ("Undergraduates", 3)]
    rows = []
    for label, t in tiers:
        group = sorted([a for a in people["alumni"] if tier(a) == t], key=year)
        if not group:
            continue
        faces = "".join(
            f'<li class="alum-face" tabindex="0">{alum_pic(a, k)}<span class="alum-name">{e(a["name"])}</span>'
            f'<span class="alum-card"><b>{e(a["name"])}</b><span>{e(a["role"])}</span>'
            f'{("<span>" + ("" if a.get("is_bio") else "Project: ") + e(a["project"]) + "</span>") if a.get("project") else ""}'
            f'{("<span>Now: " + e(a["now"]) + "</span>") if a.get("now") else ""}</span></li>' for k, a in enumerate(group))
        rows.append(f'<div class="alum-row" data-reveal><h3 class="sub">{label}</h3><ul class="alum-faces">{faces}</ul></div>')
    alumni = "".join(rows)
    body = f"""{window('assets/banners/team.webp', '<h1 data-hero>Introducing the <span class="wiggle" aria-label="Squad">' + ''.join(f'<span style="--i:{k}" aria-hidden="true">{ch}</span>' for k, ch in enumerate('Squad')) + '</span></h1>', h=BANNER_H, cls='team-hero', tag='Gaia Lab at MIT, 2025')}
<section class="section">{person(pi, pi_extra)}</section>
<section class="opps-banner"><div class="ticker" aria-label="News"><span class="ticker-tag">Hiring</span><div class="ticker-win"><div class="ticker-track"><span>2026 update: we are hiring! We are searching for a graduate student for fall 2027.</span><span aria-hidden="true">2026 update: we are hiring! We are searching for a graduate student for fall 2027.</span></div></div></div><div class="opps-in" id="opportunities"><div class="opps-head" data-reveal><h2 class="h2">Come work with us</h2><p>We are always looking for creative and motivated people to work with us. Have a look around and see if you find any projects interesting, and that overlap with your research goals.</p></div>
<ul class="ways-pills">
<li class="way" tabindex="0"><span class="way-btn">Graduate research</span><div class="way-bubble"><p>MIT EAPS accepts PhD <a href="https://eaps.mit.edu/education/graduate-program/graduate-admissions/">applications</a> each fall. Keep an eye out for <a href="https://www.nsf.gov/funding/initiatives/grfp">NSF GRFP</a> application deadlines in the fall. Please contact me or any group member with your CV and interests.</p></div></li>
<li class="way" tabindex="0"><span class="way-btn">Postdoctoral research</span><div class="way-bubble"><p>There are a few options! EAPS has a <a href="https://eaps.mit.edu/research/postdoctoral-training/">Distinguished Postdoctoral Fellowship</a> and hosts the <a href="https://www.hsfoundation.org/programs/science/51-pegasi-b-fellowship/">51 Pegasi b Fellowship</a> or the MIT School of Science fellowship (applications due each fall). You can also reach out to collaborate on a NASA or NSF proposal (or any other sources)!</p><p><a href="https://docs.google.com/spreadsheets/d/1fpsPL2yb56wYmncEIYMf5oW-vTCRgzrtIYCPqF3P50o/edit?usp=sharing">Here is a sheet I made to help you find sources of funding to work with us!</a></p></div></li>
<li class="way" tabindex="0"><span class="way-btn">Undergraduate research</span><div class="way-bubble"><p>Look through MIT's <a href="https://urop.mit.edu/">UROP</a> or <a href="https://oge.mit.edu/msrp/">MSRP</a> programs and contact me or any group member with your CV and interests.</p></div></li>
</ul></div></section>
{groups}
<section class="section"><div class="group-head" data-reveal><h2 class="h2">Group Mascot</h2></div>{person(people['mascot'])}</section>
{dots()}
<section class="section alumni-sec"><div class="group-head" data-reveal><h2 class="h2">Alumni</h2></div><div class="alumni-tiers">{alumni}</div><div>
<div class="actions" style="justify-content:center;margin-top:72px">{btn('Join us', link('contact-cv'))}</div></div></section>"""
    page("team", "Team", body, "Meet the members and alumni of the Gaia Lab at MIT.")


# ======================================================================= Themes
def flip_circle(t):
    first = md(t["q"][0])
    return (f'<li class="flip" id="{t["id"]}"><button type="button" class="flip-in" aria-label="{e(t["name"])}: show description">'
            f'<span class="face front">{img(t["img"], "")}</span>'
            f'<span class="face back"><span>{first}</span></span></button>'
            f'<span class="flip-name">{e(t["name"])}</span></li>')


def themes_page():
    set_depth("themes")
    main = [t for t in themes if t.get("main")]
    other = [t for t in themes if not t.get("main")]
    rows = []
    for i, t in enumerate(main):
        qs = "".join(f'<li data-q><span class="qn">{k + 1}</span><span class="qt">{md(q)}</span></li>' for k, q in enumerate(t["q"]))
        rows.append(f"""<article class="theme" id="{t['id']}"><div class="theme-row{' alt' if i % 2 else ''}" data-theme>
<svg class="theme-lines" aria-hidden="true"></svg>
<div class="theme-art">{pic(t['img'], t['name'], 'round')}<a class="credit" href="{e(t['credit_url'])}">{e(t['credit'])}</a></div>
<div class="theme-txt"><h2 class="h2" data-reveal>{e(t['name'])}</h2><ol class="tq">{qs}</ol></div>
</div></article>""")
    body = f"""{window(misc['covers']['themes'], '<h1 data-hero>Research Themes</h1><p class="hero-lede" data-hero>These are the <strong>main areas</strong> of our research. For each one, I have listed three broad research questions I am interested in addressing. I am always open to learning new ways to answer these, or, even better, answering newer and better research questions!</p>', h=BANNER_H, cls='shift', pos='50%', tag='Fogo, Cape Verde, 2025')}
{''.join(rows)}
{dots()}
<section class="section" id="other"><div class="grid">
<div class="c-2-12 center-head" data-reveal><h2 class="h2">Other stuff I'm interested in</h2><p class="muted">Hover over (or tap) a circle to read what draws me to it.</p></div>
<ul class="flips">{''.join(flip_circle(t) for t in other)}</ul>
</div></section>
<section class="section"><div class="grid">
<div class="c-1-5 self-center" data-reveal><h2 class="h2">Grow a river network</h2>
<p>What happens if you let it rain? Click the button below to form your very own (random) drainage network. In this mini model, water finds the lowest path, gathers into streams, joining into progressively larger rivers. Every landscape is unique!</p>
<div class="actions"><button class="btn" type="button" id="drainage-again">Grow another <span class="arr" aria-hidden="true">→</span></button></div>
<div class="actions model-tools"><button class="btn line" type="button" id="drainage-noise">Add noise</button><button class="btn line" type="button" id="drainage-craters">Add craters</button><button class="btn line" type="button" id="drainage-volcanoes">Add volcanoes</button></div></div>
<div class="c-6-13 model gap-m"><canvas id="drainage" role="img" aria-label="A simulated river drainage network spreading across contoured terrain"></canvas></div>
</div></section>"""
    page("themes", "Themes", body, "Research themes and the questions that keep the Gaia Lab up at night.")


# ======================================================================= Publications
def authors_html(names):
    bold = set(people["group_members_for_bold"])
    out = [f"<b>{e(n)}</b>" if n in bold else e(n) for n in names]
    if len(out) > 8:
        gi = [i for i, n in enumerate(names) if n in bold]
        return ", ".join(out[i] for i in sorted(set([0, 1] + gi))) + " et al."
    return ", ".join(out[:-1]) + " & " + out[-1] if len(out) > 1 else out[0]


def publications():
    set_depth("publications")
    years = sorted({p["year"] for p in pubs}, reverse=True)
    jump = "".join(f'<a href="#y{y}">{y}</a>' for y in years)
    groups = []
    for y in years:
        items = []
        for p in [p for p in pubs if p["year"] == y]:
            figs = ""
            if p["figures"]:
                n = len(p["figures"])
                figs = f'<div class="figs n{min(n, 4)}" data-gallery>' + "".join(
                    f'<button type="button" class="{"more" if i >= 4 else ""}"{f' data-more="+{n - 4}"' if i == 3 and n > 4 else ""} aria-label="Enlarge figure {i + 1}">{img(f, f"Figure {i + 1} from {p["title"]}")}<img class="ct" src="{e(media(f))}" alt="" aria-hidden="true" loading="lazy" decoding="async"></button>'
                    for i, f in enumerate(p["figures"])) + "</div>"
            summary = f'<p class="sum">{md(e(p["summary"], quote=False))}</p>' if p.get("summary") else ""
            items.append(f"""<article class="pub paper{'' if figs else ' nofig'}" data-reveal>
<div class="txt"><p class="jr">{e(p['journal'])}</p><h3>{e(p['title'])}</h3>
<p class="authors">{authors_html(p['authors'])}</p>{summary}
<div><a class="btn line" href="{e(p['url'])}">Read the paper <span class="arr" aria-hidden="true">→</span></a></div></div>
{figs}
</article>""")
        groups.append(f'<div class="year-group"><h2 class="year" id="y{y}">{y}</h2>{"".join(items)}</div>')
    body = f"""{window(misc['covers']['publications'], '<h1 data-hero class="book" aria-label="Publications"><span class="pg l" aria-hidden="true">Publi</span><span class="pg r" aria-hidden="true">cations</span></h1><p class="hero-lede" data-hero>Check out our peer-reviewed articles below! Browse the summaries and key figures, ordered chronologically. Authors in <strong>bold</strong> are group members. Hover over a figure to expand it, click to see it full size, and feel free to reach out if you need access to a paper.</p>', h=BANNER_H, cls='shift', tag='Harvard Library')}
<div class="yearnav"><div class="in"><nav class="years" aria-label="Jump to year">{jump}</nav><label class="pub-find"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="M15.5 15.5 21 21"/></svg><input id="pub-search" type="search" placeholder="Search" aria-label="Search papers" autocomplete="off"></label></div></div>
<section class="section"><div class="grid"><div>{''.join(groups)}</div></div></section>"""
    page("publications", "Publications", body, "Peer-reviewed articles from the Gaia Lab, with summaries and key figures.")


# ======================================================================= Teaching & Outreach
def outreach():
    """Teaching, outreach talks and press coverage on one page."""
    set_depth("outreach")
    v1, t1 = yt("mUoPht9wXok")
    def course_media(c):
        if c.get("video"):
            v, t = yt(c["video"])
            return embed(v, t, c.get("caption", c["code"])) + (f'<p class="cap">{e(c["caption"])}</p>' if c.get("caption") else "")
        if c.get("images"):
            return ('<div class="course-logos">' + "".join(f'<figure>{img(u, a)}</figure>' for u, a in c["images"]) + "</div>"
                    + (f'<p class="cap">{e(c["caption"])}</p>' if c.get("caption") else ""))
        return '<div class="media-soon" aria-hidden="true"><span>Photos and video coming soon</span></div>'  # placeholder until Gaia sends media
    def course(i, c):
        m = course_media(c)
        text = (f'<h3 class="sub"><span class="course-code">{e(c["code"])}</span> {e(c["name"])}</h3>'
                f'<p class="small muted">{e(c["taught"])}</p><p>{e(c["desc"])}</p>'
                f'<div class="actions">{btn("MIT course catalog", e(c["url"]), "line")}</div>')
        if m:
            return f'<div class="grid course-item"><div class="c-1-6" data-reveal>{text}</div><div class="c-7-13 course-media" data-reveal="1">{m}</div></div>'
        return f'<div class="grid course-item"><div class="c-1-6" data-reveal>{text}</div></div>'
    # Courses with a photo or video come first. Courses still waiting for media sit side by side in the
    # last rows with no placeholder box; each moves up on its own once it gets "images" or "video".
    with_media = [c for c in misc["courses"] if c.get("images") or c.get("video")]
    no_media = [c for c in misc["courses"] if not (c.get("images") or c.get("video"))]
    def course_text(c):
        return (f'<h3 class="sub"><span class="course-code">{e(c["code"])}</span> {e(c["name"])}</h3>'
                f'<p class="small muted">{e(c["taught"])}</p><p>{e(c["desc"])}</p>'
                f'<div class="actions">{btn("MIT course catalog", e(c["url"]), "line")}</div>')
    pairs = []
    for k in range(0, len(no_media), 2):
        cells = [f'<div class="c-1-6" data-reveal>{course_text(no_media[k])}</div>']
        if k + 1 < len(no_media):
            cells.append(f'<div class="c-7-13" data-reveal="1">{course_text(no_media[k + 1])}</div>')
        pairs.append(f'<div class="grid course-item course-pair">{"".join(cells)}</div>')
    courses = "".join(course(i, c) for i, c in enumerate(with_media)) + "".join(pairs)
    out = [("Pt6uvfet2N8", 0, "News video on our work published in Nature on lake outflows."),
           ("vLDQRo_Qp6s", 0, "5 minute flash talk for an interview on my research."),
           ("JnODU5J767c", 0, "MIT Alumni Forum talk on decoding the mystery of water on Mars, 2025.")]
    vids = "".join(f'<div data-reveal="{i}">{embed(yt(v, s)[0], yt(v, s)[1], c)}<p class="cap">{e(c)}</p></div>' for i, (v, s, c) in enumerate(out))
    by_year = {}
    for p in misc["press"]:
        by_year.setdefault(p["year"], []).append(p)
    tl = []
    for y in sorted(by_year, reverse=True):
        tl.append(f'<h2 class="tl-year" id="m{y}">{y}</h2>')
        for p in by_year[y]:
            tl.append(f"""<article class="tl-item" data-reveal>
<a class="pic" href="{e(p['url'])}" tabindex="-1" aria-hidden="true">{img(p['img'], '')}</a>
<div><a class="btn" href="{e(p['url'])}">{e(p['outlet'])}</a><h3>“{e(p['title'])}”</h3><p class="muted">by {e(p['author'])}</p></div>
</article>""")
    jump = '<nav class="sec-jump" aria-label="On this page"><a href="#teaching">Teaching</a><a href="#talks">Outreach</a><a href="#media">In the media</a></nav>'
    body = f"""{window('assets/banners/engagement-2.webp', '<h1 data-hero>Engagement</h1>', h=BANNER_H, cls='shift eng', tag='EPS Department, Harvard University')}
<section class="section" id="teaching"><div class="grid">
<div class="c-1-8" data-reveal><h2 class="h2">Teaching</h2></div></div>
<div class="courses">{courses}</div></section>
{dots()}
<section class="section" id="talks"><div class="grid">
<div class="c-1-7" data-reveal><h2 class="h2">Outreach</h2></div>
</div>
<div class="grid course-item legoscape-row"><div class="c-1-6 self-center" data-reveal>
<h3 class="sub">Building Mars in Lego</h3>
<p>A community-built Lego model of the surface of Mars, made from real mission data. Elevation comes from the MOLA global topography and colours come from the USGS geologic map of Mars (Tanaka et al., 2014), each resampled to a 96 by 48 grid of 2x2 plates on 18 baseplates. Every plate of height stands for about 2 km of elevation, so the tallest Tharsis volcanoes stand 13 to 14 plates high. Members of the EAPS community build it plate by plate from printed guides.</p>
<div class="actions">{btn('Visit the Building Mars website', 'https://buildingmars.thegaialab.com', 'line')}</div>
</div><div class="c-7-13 self-center" data-reveal="1"><canvas class="legoscape" data-src="{rel('assets/legoscape.json')}" aria-label="Rotatable 3D preview of the Mars Lego model" role="img"></canvas><p class="cap">The planned model, with relief doubled for this preview. Drag to turn it.</p></div></div>
<div class="grid">
<div class="trio" style="margin-top:48px">{vids}</div>
</div></section>
{dots()}
<section class="section" id="media"><div class="grid">
<div class="c-2-12" data-reveal><h2 class="h2">In the media</h2><p class="muted">Here you can find the latest, major news articles and other media about our research. Click the button to read more!</p></div>
</div></section>
<section class="section" style="padding-top:0"><div class="tl">{''.join(tl)}</div></section>"""
    page("outreach", "Engagement", body, "Teaching, outreach talks and news coverage of the Gaia Lab's research.")


# ======================================================================= Fieldwork
FIELD_TEXT = {
    "Azores": "Coastal mapping (drone and boulder analysis) of <strong><em>Lajes do Pico, Fajã da Caldeira de Santo Cristo</em></strong>, and <strong><em>Santa Maria</em></strong>.",
    "Northeast Iceland": "Drone mapping and cosmogenic He-3 dating of the <strong><em>Jökulsá á Fjöllum</em></strong> canyon. See publication <a href=\"https://doi.org/10.1016/j.epsl.2018.10.026\">here</a>.",
    "Lanzarote": "Field trip with the NASA <a href=\"https://science.nasa.gov/blogs/notes-from-the-field/2018/01/11/goddard-instrument-field-team/\">Goddard Instrument Field Team (GIFT)</a>.",
    "São Nicolau": "Reconnaissance work on landscape evolution.",
    "Lonar": "Fieldwork in conjunction with Kerala University, led by Emily Bamber, to understand the <strong><em>Lonar Crater</em></strong> lake evolution.",
    "Fogo": "Fieldwork in <strong><em>Fogo island</em></strong> with MIT students/postdocs, including Shaalin Sehra's research on drainage initiation.",
}


# Masonry tile shapes, cycled through each trip: aspect ratios as width/height
COLLAGE = ["4/3", "3/4", "3/2", "1/1", "2/3", "4/3", "4/5", "16/10", "3/4", "1/1", "3/2", "2/3"]


def _ratio(r):
    a, b = r.split("/")
    return float(a) / float(b)


def _tree(seq, target, rnd):
    """Random slicing tree over a run of photos, steered toward a target aspect ratio (w/h)."""
    n = len(seq)
    if n == 1:
        return seq[0]
    k = rnd.randint(1, n - 1)
    horiz = rnd.random() < (0.8 if target > 1 else 0.2)  # side by side when the box is wide
    if horiz:
        return ("h", _tree(seq[:k], target * k / n, rnd), _tree(seq[k:], target * (n - k) / n, rnd))
    return ("v", _tree(seq[:k], target * n / k, rnd), _tree(seq[k:], target * n / (n - k), rnd))


def _ar(node, ars):
    if isinstance(node, int):
        return ars[node]
    a, b = _ar(node[1], ars), _ar(node[2], ars)
    return a + b if node[0] == "h" else 1 / (1 / a + 1 / b)


def _place(node, ars, x, y, w, h, out):
    if isinstance(node, int):
        out[node] = (x, y, w, h)
        return
    a, b = _ar(node[1], ars), _ar(node[2], ars)
    if node[0] == "h":
        wa = w * a / (a + b)
        _place(node[1], ars, x, y, wa, h, out); _place(node[2], ars, x + wa, y, w - wa, h, out)
    else:
        ha = h * (1 / a) / (1 / a + 1 / b)
        _place(node[1], ars, x, y, w, ha, out); _place(node[2], ars, x, y + ha, w, h - ha, out)


def collage_layout(ars, target, seed, tries=6000):
    """Pack photos into one rectangle with no cropping: every tile keeps its photo's shape, the block ends flush.
    Picks the tree closest to the target shape with a good spread of tile sizes."""
    import math
    import random
    rnd = random.Random(seed)
    n, best = len(ars), None
    for _ in range(tries):
        t = _tree(list(range(n)), target, rnd)
        ar = _ar(t, ars)
        out = [None] * n
        _place(t, ars, 0, 0, 1, 1 / ar, out)
        areas = [w * h for _, _, w, h in out]
        mean = sum(areas) / n
        logs = [math.log(a / mean) for a in areas]
        spread = (sum(v * v for v in logs) / n) ** .5
        score = 3 * abs(math.log(ar / target)) + 2 * abs(spread - .55) + 4 * sum(max(0, -v - 1.0) for v in logs) + 2 * sum(max(0, v - 1.5) for v in logs)
        if best is None or score < best[0]:
            best = (score, ar, out)
    _, ar, out = best
    return ar, [(x * 100, y * ar * 100, w * 100, h * ar * 100) for x, y, w, h in out]  # percent of container width / height


def collage(t):
    ratios = t.get("ratios") or [COLLAGE[k % len(COLLAGE)] for k in range(len(t["photos"]))]
    ars = [_ratio(r) for r in ratios]
    ar, desk = collage_layout(ars, 0.78, t["place"])
    mar, mob = collage_layout(ars, 0.32, t["place"] + "-m")
    items = []
    for k, u in enumerate(t["photos"]):
        (x, y, w, h), (mx, my, mw, mh) = desk[k], mob[k]
        st = f"--x:{x:.3f}%;--y:{y:.3f}%;--w:{w:.3f}%;--h:{h:.3f}%;--mx:{mx:.3f}%;--my:{my:.3f}%;--mw:{mw:.3f}%;--mh:{mh:.3f}%"
        items.append(f'<button type="button" class="jg-item" style="{st}" aria-label="Enlarge photo {k + 1}">{img(u, f"{t["place"]} {t["year"]}, photo {k + 1}")}</button>')
    return f'<div class="jg collage"><div class="cg" data-gallery style="--ar:{ar:.4f};--mar:{mar:.4f}">' + "".join(items) + "</div></div>"


def fieldwork():
    set_depth("fieldwork")
    trips = "".join(f"""<section class="trip-panel" id="{trip_slug(t['place'])}" hidden><div class="grid"><div class="c-1-8"><h2 class="h2">{e(trip_title(t['place']))}</h2><p class="trip-year">{t.get('kind', 'Fieldwork')}, {t['year']}</p><p>{FIELD_TEXT[t['place']]}</p></div></div>
{collage(t)}</section>""" for t in misc["fieldwork"])
    body = f"""<section class="globe-hero"><div class="story intro field-intro">
<div class="story-text" data-reveal><h1>Gallery</h1>
<p>Our most recent adventures. Spin the globe and click a pin to open the photos from that trip. Hopefully, many more to come!</p></div>
<div class="story-art" data-reveal="1">{globe_block(big=True)}<span class="globe-hint">Click on a location!</span></div>
</div></section>
{trips}"""
    page("fieldwork", "Gallery", body, "Fieldwork sites and photos from the Gaia Lab.")
    for t in misc["fieldwork"]:
        sl = trip_slug(t["place"])
        set_depth(sl)
        body = f"""<section class="section tight"><div class="grid"><div class="c-1-8" data-reveal><h1 class="h2">{e(trip_title(t['place']))}</h1><p class="trip-year">{t.get('kind', 'Fieldwork')}, {t['year']}</p><p>{FIELD_TEXT[t["place"]]}</p>
<div class="actions">{btn("Back to the globe", link("fieldwork"), "line")}</div></div></div>
{collage(t)}</section>"""
        page(sl, trip_title(t["place"]), body, f"Photos from our {t['year']} fieldwork in {trip_title(t['place'])}.")


# ======================================================================= Gallery
def gallery():
    set_depth("gallery")
    art = "".join(f'<figure data-reveal="{i % 2}"><button type="button" aria-label="Enlarge artwork">{img(g["img"], g["cap"])}</button><figcaption class="cap">{e(g["cap"])}</figcaption></figure>'
                  for i, g in enumerate(misc["gallery"]))
    body = f"""{window(misc['covers']['gallery'], '<h1>Gallery</h1>', h='64vh')}
<section class="section"><div class="grid">
<p class="lede c-2-12" data-reveal>A very random assortment of creative projects. Some space-related, some landscape- or geology-related... The captions provide a bit of context, but not much!</p></div></section>
<section class="section" style="padding-top:0"><div class="grid"><div class="art" data-gallery>{art}</div></div></section>"""
    page("gallery", "Gallery", body, "Science-themed art and creative projects from the Gaia Lab.")


# ======================================================================= Resources
def resources():
    set_depth("resources")
    r = misc["resources"]
    m = r["models"][0]
    sketch = f'{embed("https://sketchfab.com/models/" + m["url"].rsplit("-", 1)[-1] + "/embed?autostart=1", m.get("thumb", ""), m["title"])}'
    body = f"""{window(None, '<canvas class="mesh" data-src="' + rel('assets/mars-mesh.json') + '" aria-hidden="true"></canvas><h1>Data &amp; code</h1><p class="hero-lede">Please reach out if you have any data requests related to our publications or other projects!</p>', h=BANNER_H, cls='meshwin')}
<section class="section"><div class="grid">
<div class="c-1-6 self-center" data-reveal><h2 class="h2">Explore our surfaces in 3D</h2>
<p>Play around with some of our surface models in <strong>SketchFab</strong>. Here's Parana Basin on Mars, with mapped valleys and a paleolake. Press play and explore!</p></div>
<div class="c-7-13" data-reveal="1">{sketch}</div>
</div></section>
{dots()}
<section class="section"><div class="grid">
<div class="c-1-6 self-center" data-reveal><h2 class="h2">MESA</h2>
<p>Coming soon! Check this space:</p>
<div class="actions">{btn('planetarydems.org', 'https://planetarydems.org', 'line')}</div></div>
<div class="c-7-13" data-reveal="1"><div class="mars-wrap"><canvas id="mars" width="400" height="400" data-tex="{rel('assets/mars-mola.jpg')}" role="img" aria-label="A turning globe of Mars coloured by elevation"></canvas></div></div>
</div></section>"""
    page("resources", "Data & code", body, "Data, code and 3D models from the Gaia Lab.")


# ======================================================================= Contact / CV
def contact():
    set_depth("contact-cv")
    osm = "https://www.openstreetmap.org/export/embed.html?bbox=-71.0935%2C42.3586%2C-71.0852%2C42.3622&amp;layer=mapnik&amp;marker=42.360401%2C-71.089331"
    body = f"""<section class="section contact"><div class="grid contact-grid">
<div class="c-1-7" data-reveal><h1 class="h2">Get in touch</h1>
<div class="actions"><a class="btn" href="#" data-m="dWRlLnRpbUBzYWlhZw==">Send me an email <span class="arr" aria-hidden="true">→</span></a><button class="btn line" type="button" id="copy-email" data-m="dWRlLnRpbUBzYWlhZw==">Copy address</button></div>
<div class="contact-row"><div><h3 class="sub">Lab</h3><p>Room 54-319, Green Building<br>Massachusetts Institute of Technology<br>77 Massachusetts Avenue, Cambridge, MA 02139</p><p>Gaia's office is in Room 54-510.</p></div>
<div><h3 class="sub">CV</h3><p>My most up-to-date CV.</p>{btn('View & download', media(misc['cv']), 'line')}</div></div></div>
<div class="c-8-13 contact-art" data-reveal="1">{pic('assets/paper-plane.webp', 'Paper airplane', 'cutout', eager=True)}<div class="map"><iframe src="{osm}" title="Map of the MIT Green Building" loading="lazy"></iframe></div></div>
</div></section>"""
    page("contact-cv", "Contact/CV", body, "How to reach Gaia Stucky de Quay and the Gaia Lab.")


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for f in (home, team, themes_page, publications, outreach, fieldwork, resources, contact):
        f()
    if MODE == "pane":
        (OUT / "pages.json").write_text(json.dumps(PAGES))
    print("Built", len(NAV), "pages into", OUT)
