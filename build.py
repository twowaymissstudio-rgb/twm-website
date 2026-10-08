#!/usr/bin/env python3
"""Build the Two Way Miss Studio site from listings.json.

Run from the repository folder:   python3 build.py

It writes index.html, one page per listing at listing/<slug>/index.html,
sitemap.xml and robots.txt. Photos live in img/ (large, ~1600px) and
img/t/ (thumbnails, ~800px). Missing thumbnails are made automatically
when Pillow is installed.
"""
import html
import json
import os
import shutil
from datetime import date
from urllib.parse import urlencode

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(open(os.path.join(ROOT, "listings.json"), encoding="utf-8"))
SITE, CATS, LISTINGS = DATA["site"], DATA["categories"], DATA["listings"]
HOME = DATA.get("home", {})
YEAR = date.today().year
e = lambda s: html.escape(str(s), quote=True)


def make_thumbs():
    try:
        from PIL import Image, ImageOps
    except ImportError:
        return
    os.makedirs(os.path.join(ROOT, "img", "t"), exist_ok=True)
    for f in os.listdir(os.path.join(ROOT, "img")):
        src = os.path.join(ROOT, "img", f)
        dst = os.path.join(ROOT, "img", "t", f)
        if f.lower().endswith(".jpg") and not os.path.exists(dst):
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            im.thumbnail((800, 800))
            im.save(dst, quality=78, optimize=True)


def check_photos():
    missing = []
    for l in LISTINGS:
        for f, _ in l["photos"]:
            if not os.path.exists(os.path.join(ROOT, "img", f)):
                missing.append(f"{l['slug']}: img/{f}")
    for f in [HOME.get("hero"), HOME.get("city_cover")] + [x[0] for x in HOME.get("process", [])] + [x[0] for x in DATA.get("delivered", [])]:
        if f and not os.path.exists(os.path.join(ROOT, "img", f)):
            missing.append(f"home page: img/{f}")
    if missing:
        raise SystemExit("Missing photos:\n  " + "\n  ".join(missing))


LOGO = ('<svg viewBox="0 0 40 40" fill="none" stroke="currentColor" stroke-width="2.2" aria-hidden="true">'
        '<circle cx="20" cy="20" r="18" stroke-width="1.4"/>'
        '<path d="M8 20h24M8 20l6-6M8 20l6 6M32 20l-6-6M32 20l-6 6"/></svg>')


def page(title, desc, body, p, canonical, og_image):
    """p is the relative prefix back to the site root ('' or '../../')."""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{e(canonical)}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{e(og_image)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Figtree:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{p}style.css">
</head>
<body>
<div class="wrap">
<header class="top">
  <a class="mark" href="{p}./" aria-label="Two Way Miss Studio home">{LOGO}
    <span><b>Two Way Miss</b><small>Golf course art · Gilbert, AZ</small></span></a>
  <nav aria-label="Sections">
    <a href="{p}./#shop">Shop</a><a href="{p}./#process">Process</a><a href="{p}./#commission">Commission</a>
    <a href="{e(SITE['etsy'])}" target="_blank" rel="noopener">Etsy ↗</a>
  </nav>
</header>
{body}
<footer>
  <span>© {YEAR} Two Way Miss Studio LLC · Gilbert, Arizona</span>
  <span><a href="{e(SITE['etsy'])}" target="_blank" rel="noopener">Etsy shop</a></span>
</footer>
</div>
<dialog id="lb" aria-label="Photo viewer">
  <div class="lb">
    <img id="lb-img" alt="">
    <div class="bar">
      <div><h3 id="lb-t"></h3><p id="lb-m"></p></div>
      <div class="nav"><button id="lb-p" aria-label="Previous photo">←</button><button id="lb-n" aria-label="Next photo">→</button><button id="lb-x" aria-label="Close">✕</button></div>
    </div>
  </div>
</dialog>
<script src="{p}site.js"></script>
</body>
</html>
"""


def card(l, p):
    photos = l["photos"]
    alt_img = (f'<img class="alt" src="{p}img/t/{e(photos[1][0])}" alt="" loading="lazy">'
               if len(photos) > 1 else "")
    count = f'<span class="count">{len(photos)} photos</span>' if len(photos) > 1 else ""
    return f"""<a class="card" href="{p}listing/{e(l['slug'])}/" data-c="{e(l['category'])}">
  <div class="ph"><img src="{p}img/t/{e(photos[0][0])}" alt="{e(photos[0][1])}" loading="lazy">{alt_img}{count}</div>
  <span class="chip">{e(CATS[l['category']])}</span>
  <h3>{e(l['title'])}</h3>
  <p class="loc">{e(l['location'])}</p>
</a>"""


def build_index():
    by_cat = {c: [l for l in LISTINGS if l["category"] == c] for c in CATS}
    cover = lambda c, fallback: by_cat[c][0]["photos"][0][0] if by_cat[c] else fallback
    hero = next((l for l in LISTINGS if l["slug"] == HOME.get("hero_listing")), LISTINGS[0])
    hero_img = HOME.get("hero") or hero["photos"][0][0]
    hero_alt = next((a for f, a in hero["photos"] if f == hero_img), hero["title"])
    hero_score = "".join(f"<span>{e(k)}<b>{e(v)}</b></span>" for k, v in (HOME.get("hero_specs") or hero["specs"])[:4])
    city_cover = HOME.get("city_cover") or cover("city", "IMG_2539.jpg")
    process = "".join(f'<img src="img/t/{e(f)}" alt="{e(a)}" loading="lazy">' for f, a in HOME.get("process", []))
    filters = '<button data-f="all" aria-pressed="true">All</button>' + "".join(
        f'<button data-f="{c}" aria-pressed="false">{e(n)}</button>' for c, n in CATS.items())
    delivered = "".join(f'<img src="img/t/{e(f)}" alt="{e(a)}" loading="lazy">' for f, a in DATA["delivered"])
    types = "".join(f"<option>{e(t)}</option>" for t in
                    ["Hole-in-one plaque", "Full course map", "Single signature hole", "City or coastline map"])
    body = f"""
<div class="hero" id="top">
  <div>
    <p class="eyebrow">Layered wood maps · cut & engraved by hand</p>
    <h1>Your course, <em>cut in layers.</em></h1>
    <p class="lede">Two Way Miss Studio turns the holes you play into layered wood art. Fairways, greens, bunkers and water are cut from wood, engraved, painted and assembled by hand. Each piece records the hole, the yardage and the day.</p>
    <div class="ctas">
      <a class="btn" href="#shop">Browse the work</a>
      <a class="btn ghost" href="#commission">Start a custom map</a>
    </div>
  </div>
  <a class="plaque" href="listing/{e(hero['slug'])}/" style="display:block;text-decoration:none;color:inherit">
    <img src="img/{e(hero_img)}" alt="{e(hero_alt)}">
    <span class="scorecard">
      {hero_score}
    </span>
  </a>
</div>

<section id="collections">
  <div class="sechead">
    <div><p class="eyebrow">Collections</p><h2>Three ways to keep a place</h2></div>
    <p>Every piece starts from real map data. It is scaled to the frame and built in layers you can feel.</p>
  </div>
  <div class="cols">
    <button class="col" data-go="ace">
      <div class="ph"><img src="img/t/{cover('ace','IMG_2237.jpg')}" alt="" loading="lazy"></div>
      <span class="eyebrow"><span>Hole-in-one</span><span>{len(by_cat['ace'])} listings</span></span>
      <h3>The ace plaque</h3>
      <p>The hole you aced, with your name, the date, the yardage and the club you hit.</p>
    </button>
    <button class="col" data-go="course">
      <div class="ph"><img src="img/t/{cover('course','IMG_1821.jpg')}" alt="" loading="lazy"></div>
      <span class="eyebrow"><span>Course maps</span><span>{len(by_cat['course'])} listings</span></span>
      <h3>The full course</h3>
      <p>Your home club or a bucket-list major, every hole in its place, with par and total yardage.</p>
    </button>
    <button class="col" data-go="city">
      <div class="ph"><img src="img/t/{e(city_cover)}" alt="" loading="lazy"></div>
      <span class="eyebrow"><span>City & coast</span><span>{len(by_cat['city'])} listings</span></span>
      <h3>Hometowns</h3>
      <p>Street grids, shorelines and lakes for the places that matter to you, from Gilbert to Santa Cruz.</p>
    </button>
  </div>
</section>

<section id="shop">
  <div class="sechead">
    <div><p class="eyebrow">The work · {len(LISTINGS)} pieces</p><h2>Browse the work</h2></div>
    <div class="filters" role="group" aria-label="Filter pieces">{filters}</div>
  </div>
  <div class="shop" id="shopgrid">
{chr(10).join(card(l, '') for l in LISTINGS)}
  </div>
</section>

<section id="process">
  <div class="sechead">
    <div><p class="eyebrow">Process</p><h2>From satellite to wall</h2></div>
    <p>Every map goes through the same four steps in the studio in Gilbert, Arizona.</p>
  </div>
  <div class="steps">
    <div class="step"><span class="n">STEP 1</span><h3>Map the ground</h3><p>Fairways, greens, bunkers, water and cart paths are traced from OpenStreetMap data, so every shape matches the real course.</p></div>
    <div class="step"><span class="n">STEP 2</span><h3>Draw the piece</h3><p>The layout is redrawn in Illustrator with hole badges, a yardage scale and lettering in the club's own style.</p></div>
    <div class="step"><span class="n">STEP 3</span><h3>Cut & engrave</h3><p>Each layer is laser cut from Baltic birch. Bunkers get depth from graded engraving, and mowing lines are etched into the greens.</p></div>
    <div class="step"><span class="n">STEP 4</span><h3>Finish by hand</h3><p>Layers are stained, painted and sealed, then assembled with raised trees and framed for the wall or the desk.</p></div>
  </div>
  <div class="detail">{process}</div>
</section>

<section id="clients">
  <div class="sechead">
    <div><p class="eyebrow">Delivered</p><h2>In good hands</h2></div>
    <p>A few of the golfers who now have their ace on the wall.</p>
  </div>
  <div class="people">{delivered}</div>
</section>

<section id="commission" class="commission">
  <div>
    <p class="eyebrow">Commission</p>
    <h2 style="font-size:clamp(34px,4.6vw,56px)">Made a hole-in-one?<br>Let's make it permanent.</h2>
    <ul>
      <li>Any course with mapped holes, anywhere in the world.</li>
      <li>Natural birch, white or grey finishes.</li>
      <li>Your name, date, yardage and club engraved on the piece.</li>
      <li>A proof to approve before anything is cut.</li>
    </ul>
  </div>
  <form id="req" novalidate>
    <label class="full" for="f-type">What would you like<select id="f-type">{types}</select></label>
    <label class="full" for="f-course">Course or place<input id="f-course" placeholder="Seville Golf & Country Club, Gilbert AZ"></label>
    <label for="f-hole">Hole<input id="f-hole" placeholder="17"></label>
    <label for="f-date">Date<input id="f-date" type="date"></label>
    <label for="f-yds">Yards<input id="f-yds" inputmode="numeric" placeholder="147"></label>
    <label for="f-club">Club<input id="f-club" placeholder="7 iron"></label>
    <label class="full" for="f-name">Name on the plaque<input id="f-name" placeholder="Your name"></label>
    <label class="full" for="f-notes">Anything else<textarea id="f-notes" placeholder="Finish, size, a gift deadline…"></textarea></label>
    <pre id="out" hidden></pre>
    <div class="full" style="display:flex;gap:10px;flex-wrap:wrap">
      <button class="btn" type="submit">Copy my request</button>
      <a class="btn ghost" href="{e(SITE['etsy'])}" target="_blank" rel="noopener">Message us on Etsy ↗</a>
    </div>
    <p class="formnote" id="note">Copy your request, then paste it into a message to the shop on Etsy.</p>
  </form>
</section>
"""
    desc = "Layered wood golf course maps, hole-in-one plaques and city maps, handmade in Gilbert, Arizona."
    out = page(SITE["name"], desc, body, "", SITE["base_url"], SITE["base_url"] + "img/" + (HOME.get("hero") or LISTINGS[0]["photos"][0][0]))
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(out)


TYPE_FOR = {"ace": "Hole-in-one plaque", "hole": "Single signature hole",
            "course": "Full course map", "city": "City or coastline map"}


def build_listing(l):
    p = "../../"
    photos = l["photos"]
    single = len(photos) == 1
    thumbs = "" if single else '<div class="thumbs" role="tablist" aria-label="Photos">' + "".join(
        f'<button data-i="{i}" aria-label="Photo {i+1}" aria-current="{str(i == 0).lower()}">'
        f'<img src="{p}img/t/{e(f)}" alt="" loading="lazy"></button>' for i, (f, _) in enumerate(photos)) + "</div>"
    arrows = "" if single else ('<button class="arrow prev" aria-label="Previous photo">←</button>'
                                '<button class="arrow next" aria-label="Next photo">→</button>'
                                f'<span class="pos">1 / {len(photos)}</span>')
    specs = "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in l["specs"])
    desc_html = "".join(f"<p>{e(x)}</p>" for x in l["description"])
    etsy = l.get("etsy") or SITE["etsy"]
    etsy_label = "Buy on Etsy ↗" if l.get("etsy") else "Visit the Etsy shop ↗"
    q = "?" + urlencode({"type": TYPE_FOR[l["category"]], "course": l["location"]})
    related = [x for x in LISTINGS if x["category"] == l["category"] and x["slug"] != l["slug"]]
    related += [x for x in LISTINGS if x["category"] != l["category"]]
    related = related[:4]
    data = json.dumps({"title": l["title"], "photos": [[f, a] for f, a in photos]})
    body = f"""
<nav class="crumbs" aria-label="Breadcrumb"><a href="{p}./#shop">Shop</a><span>/</span><a href="{p}./?c={l['category']}#shop">{e(CATS[l['category']])}</a><span>/</span><span>{e(l['title'])}</span></nav>
<div class="listing">
  <div class="gallery{' single' if single else ''}" id="gallery" data-gallery='{e(data)}'>
    {thumbs}
    <div class="stage" id="stage"><img id="stage-img" src="{p}img/{e(photos[0][0])}" alt="{e(photos[0][1])}">{arrows}</div>
  </div>
  <div class="info">
    <p class="eyebrow">{e(CATS[l['category']])}</p>
    <h1>{e(l['title'])}</h1>
    <p class="loc">{e(l['location'])}</p>
    <dl class="specs">{specs}</dl>
    <div class="desc">{desc_html}</div>
    <div class="ctas">
      <a class="btn" href="{p}./{e(q)}#commission">Request one like this</a>
      <a class="btn ghost" href="{e(etsy)}" target="_blank" rel="noopener">{etsy_label}</a>
    </div>
    <p class="note">Every piece is made to order. You approve a proof before anything is cut.</p>
  </div>
</div>
<section class="related">
  <h2>More from the studio</h2>
  <div class="shop">{''.join(card(x, p) for x in related)}</div>
</section>
"""
    title = f"{l['title']} · {SITE['name']}"
    desc = " ".join(l["description"])[:200]
    url = f"{SITE['base_url']}listing/{l['slug']}/"
    d = os.path.join(ROOT, "listing", l["slug"])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(
        page(title, desc, body, p, url, SITE["base_url"] + "img/" + photos[0][0]))


def build_sitemap():
    urls = [SITE["base_url"]] + [f"{SITE['base_url']}listing/{l['slug']}/" for l in LISTINGS]
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    xml += "".join(f"  <url><loc>{e(u)}</loc></url>\n" for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w").write(xml)
    open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['base_url']}sitemap.xml\n")


if __name__ == "__main__":
    make_thumbs()
    check_photos()
    # Remove pages for listings that no longer exist.
    ldir = os.path.join(ROOT, "listing")
    if os.path.isdir(ldir):
        keep = {l["slug"] for l in LISTINGS}
        for d in os.listdir(ldir):
            if d not in keep and os.path.isdir(os.path.join(ldir, d)):
                shutil.rmtree(os.path.join(ldir, d))
    build_index()
    for l in LISTINGS:
        build_listing(l)
    build_sitemap()
    print(f"Built home page + {len(LISTINGS)} listing pages.")
