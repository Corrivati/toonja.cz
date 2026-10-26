#!/usr/bin/env python3
"""Slovník pojmů na toonja.cz.

Web zůstává čisté HTML bez buildu na hostingu. Tenhle skript je jen pomocník
pro úpravy: vygeneruje stránky slovníku do repozitáře a zkontroluje prolinkování.

  python3 tools/slovnik.py build          rozcestník + stránky pojmů + sitemap + llms.txt
  python3 tools/slovnik.py build --navrh  i pojmy ve stavu "navrh" (jen pro náhled, necommitovat)
  python3 tools/slovnik.py check          kde v článcích chybí odkaz na pojem ze slovníku
  python3 tools/slovnik.py check --vse    totéž i pro pojmy, které ještě nemají stránku

Data: slovnik/pojmy.json (registr pojmů), slovnik/_obsah/<slug>.html (text pojmu).
Hlavička a patička se berou z blog/index.html, aby slovník vypadal jako zbytek webu.
Potřebuje: pip install beautifulsoup4 lxml
"""
import html
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
SLOVNIK = ROOT / "slovnik"
BASE = "https://www.toonja.cz"

ALPHABET = ["A", "B", "C", "Č", "D", "E", "F", "G", "H", "CH", "I", "J", "K", "L", "M", "N",
            "O", "P", "Q", "R", "Ř", "S", "Š", "T", "U", "V", "W", "X", "Y", "Z", "Ž"]
FOLD = str.maketrans("ÁÉĚÍÓÚŮÝĎŤŇáéěíóúůýďťň", "AEEIOUUYDTNaeeiouuydtn")


# ---------- data ----------

def load():
    data = json.loads((SLOVNIK / "pojmy.json").read_text(encoding="utf-8"))
    return data["kategorie"], data["pojmy"]


def letter(term):
    t = term.strip().upper()
    if t.startswith("CH"):
        return "CH"
    return t[0].translate(FOLD)


def sort_key(term):
    t = term.upper()
    first = letter(t)
    rest = t[2:] if first == "CH" else t[1:]
    return (ALPHABET.index(first) if first in ALPHABET else 99, rest.translate(FOLD))


def fold(s):
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def esc(s):
    return html.escape(s, quote=True)


def term_href(p, from_hub=True):
    if p.get("url"):
        return p["url"]
    return p["slug"]


def full_label(p):
    return f'{p["pojem"]} ({p["plny_nazev"]})' if p.get("plny_nazev") else p["pojem"]


# ---------- šablona webu ----------

def site_parts():
    src = (ROOT / "blog" / "index.html").read_text(encoding="utf-8")
    soup = BeautifulSoup(src, "lxml")
    header = str(soup.select_one(".header-wrapper"))
    footer = str(soup.select_one("footer.footer-wrapper"))
    # odkazy relativní k /blog/ přepsat pro /slovnik/
    header = header.replace('href="./"', 'href="../blog/"').replace(" w--current", "")
    header = header.replace('aria-current="page" ', "")
    footer = footer.replace('href="./"', 'href="../blog/"')
    footer = footer.replace('<li class="footer-list-item"></li>',
                            '<li class="footer-list-item"><a class="footer-link" href="./">Slovník pojmů</a></li>', 1)
    tail = src[src.find("</footer>") + len("</footer>"):]
    tail = tail[tail.find("</div>") + len("</div>"):]  # zavření .page-wrapper
    tail = tail.replace("</body></html>", "").strip()
    gtag = re.search(r'<script async="" src="https://www.googletagmanager.com.*?</script><script type="text/javascript">window.dataLayer.*?</script>', src, re.S)
    return header, footer, tail, gtag.group(0) if gtag else ""


def head(title, desc, url, schema, og_type="website"):
    _, _, _, gtag = PARTS
    return f'''<!DOCTYPE html>
<html data-wf-page="65721b10eaa12f9577154f49" data-wf-site="65721b10eaa12f9577154e7a" lang="cs"><head><meta charset="utf-8"/>
<title>{esc(title)}</title>
<meta content="{esc(desc)}" name="description"/>
<meta content="{esc(title)}" property="og:title"/><meta content="{esc(desc)}" property="og:description"/>
<meta content="{esc(title)}" name="twitter:title"/><meta content="{esc(desc)}" name="twitter:description"/>
<meta content="{BASE}/assets/images/foto-toonja.jpg" property="og:image"/>
<meta content="{og_type}" property="og:type"/><meta content="summary_large_image" name="twitter:card"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<link href="{url}" rel="canonical"/><meta content="{url}" property="og:url"/>
<meta content="cs_CZ" property="og:locale"/><meta content="Marek Toonja" property="og:site_name"/>
<link href="../assets/css/seo-fixes.css" rel="stylesheet"/>
<link href="../assets/css/toonja-cz.webflow.shared.00a3468f2.css" rel="stylesheet" type="text/css"/>
<link href="../assets/css/slovnik.css" rel="stylesheet"/>
<script type="text/javascript">!function(o,c){{var n=c.documentElement,t=" w-mod-";n.className+=t+"js",("ontouchstart"in o||o.DocumentTouch&&c instanceof DocumentTouch)&&(n.className+=t+"touch")}}(window,document);</script>
<link href="../assets/images/favicon-toonja.png" rel="shortcut icon" type="image/x-icon"/>
<link href="../assets/images/napotoonja.png" rel="apple-touch-icon"/>
{gtag}
<script type="application/ld+json">{json.dumps(schema, ensure_ascii=False)}</script>
</head><body><div class="page-wrapper">
<div class="bg-secondary-5">{PARTS[0]}</div>
'''


def foot(extra_js=""):
    _, footer, tail, _ = PARTS
    return f'{footer}</div>{tail}{extra_js}</body></html>\n'


PERSON = {"@id": f"{BASE}/#marek"}


def chip(cat, kat):
    k = kat[cat]
    return f'<span class="slovnik-chip" style="--chip:{k["barva"]}"><span class="slovnik-chip__dot"></span>{esc(k["nazev"])}</span>'


def dots(prefix="blog-post"):
    return (f'<div class="bg-dot {prefix}---top-right-dot"></div>'
            f'<div class="bg-dot {prefix}---middle-left-dot"></div>'
            f'<div class="bg-dot {prefix}---middle-right-dot"></div>')


def article_info(slug):
    f = ROOT / "blog" / f"{slug}.html"
    if not f.exists():
        return None
    s = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
    h1 = s.find("h1").get_text(" ", strip=True)
    img = s.select_one(".top-section img.border-radius-28px")
    perex = s.select_one(".top-section p")
    return {"slug": slug, "title": h1, "img": img["src"] if img else "",
            "perex": perex.get_text(" ", strip=True) if perex else ""}


# ---------- rozcestník ----------

def build_hub(kat, pojmy, include_draft):
    shown = [p for p in pojmy if p["stav"] in ("hotovo", "clanek") or (include_draft and p["priorita"] == 1)]
    shown.sort(key=lambda p: sort_key(p["pojem"]))
    url = f"{BASE}/slovnik/"
    title = "Slovník pojmů online marketingu, SEO a webů | Marek Toonja"
    desc = "Co je SEO, PPC, konverze nebo MCP? Pojmy z online marketingu, e-commerce a tvorby webů vysvětlené lidsky, s příklady z praxe. Od A do Ž."

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "CollectionPage", "@id": url + "#webpage", "url": url, "name": title, "description": desc,
         "inLanguage": "cs", "isPartOf": {"@id": f"{BASE}/#website"}, "author": PERSON,
         "mainEntity": {"@id": url + "#set"}},
        {"@type": "DefinedTermSet", "@id": url + "#set", "name": "Slovník pojmů online marketingu", "url": url,
         "hasDefinedTerm": [{"@type": "DefinedTerm", "name": full_label(p), "description": p["definice"],
                             "url": (BASE + "/blog/" + p["url"].split("/")[-1]) if p.get("url") else url + p["slug"]}
                            for p in shown]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Úvod", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Slovník pojmů", "item": url}]}]}

    used_cats = [c for c in kat if any(p["kategorie"] == c for p in shown)]
    filters = ['<button class="slovnik-filter is-active" data-cat="vse" type="button">Vše</button>']
    for c in used_cats:
        filters.append(f'<button class="slovnik-filter" data-cat="{c}" type="button" style="--chip:{kat[c]["barva"]}">'
                       f'<span class="slovnik-chip__dot"></span>{esc(kat[c]["nazev"])}</button>')

    groups = {}
    for p in shown:
        groups.setdefault(letter(p["pojem"]), []).append(p)
    az = []
    for L in ALPHABET:
        if L in groups:
            az.append(f'<a class="slovnik-az__link" href="#pismeno-{L.lower()}">{L}</a>')
        else:
            az.append(f'<span class="slovnik-az__link is-empty" aria-hidden="true">{L}</span>')

    sections = []
    for L in ALPHABET:
        if L not in groups:
            continue
        cards = []
        for p in groups[L]:
            is_article = p["stav"] == "clanek"
            sub = f'<div class="slovnik-card__sub">{esc(p["plny_nazev"])}</div>' if p.get("plny_nazev") else ""
            more = "Číst článek" if is_article else "Co to je"
            cards.append(f'''<a class="card slovnik-card" href="{esc(term_href(p))}" data-cat="{p["kategorie"]}">
<div class="slovnik-card__head"><h3 class="slovnik-card__term">{esc(p["pojem"])}</h3><span class="line-rounded-icon link-icon-right">\ue805</span></div>{sub}
<p class="slovnik-card__def">{esc(p["definice"])}</p>
<div class="slovnik-card__top">{chip(p["kategorie"], kat)}{'<span class="slovnik-card__flag">Článek na blogu</span>' if is_article else ''}</div>
</a>''')
        sections.append(f'''<section class="slovnik-group" id="pismeno-{L.lower()}" data-letter="{L}">
<div class="slovnik-group__letter">{L}</div>
<div class="slovnik-list">{"".join(cards)}</div>
</section>''')

    body = f'''<div class="top-section pd-top-56px bg-secondary-5 slovnik-hero">
<div class="container-default position-relative---z-index-1 w-container">
<nav class="slovnik-breadcrumb" aria-label="Drobečková navigace"><a href="../">Úvod</a><span>/</span><span aria-current="page">Slovník pojmů</span></nav>
<div class="text-center">
<div class="inner-container _966px center"><h1 class="display-2 mg-bottom-16px">Slovník pojmů online marketingu</h1></div>
<div class="inner-container _686px center"><p class="mg-bottom-0">SEO, PPC, weby i AI bez mlžení. Každý pojem nejdřív jednou větou, pak do hloubky a s příkladem z praxe.</p></div>
</div>
</div>
{dots()}
</div>

<div class="section pd-top-64px slovnik-section">
<div class="container-default w-container">
<div class="slovnik-toolbar">
<div class="slovnik-filters" role="group" aria-label="Filtrovat podle oblasti">{"".join(filters)}</div>
<nav class="slovnik-az" aria-label="Abecední rejstřík">{"".join(az)}</nav>
</div>
<p class="slovnik-count text-200" aria-live="polite"><span id="slovnik-pocet">{len(shown)}</span> pojmů</p>
<div class="slovnik-groups">{"".join(sections)}</div>
<div class="slovnik-empty" hidden><p class="display-4 mg-bottom-8px">Tenhle pojem tu zatím nemám.</p><p class="mg-bottom-24px">Napište mi, který vám chybí. Přidám ho a dám vědět.</p><a class="btn-primary w-button" href="../contact">Navrhnout pojem</a></div>

<div class="card slovnik-cta">
<div><p class="display-3 color-neutral-100 mg-bottom-8px">Pojmy znáte. Teď výsledky.</p>
<p class="color-neutral-300 mg-bottom-0">Pomůžu vám s SEO, PPC i webem, který si spravujete sami. Bez slovníku, rovnou na věc.</p></div>
<a class="btn-primary white w-button" href="../spoluprace">Jak spolupracuji</a>
<div class="bg-dot newsletter-card---top-right-dot"></div><div class="bg-dot newsletter-card---bottom-left-dot"></div>
</div>
</div>
</div>
'''
    page = head(title, desc, url, schema) + body + foot('<script src="../assets/js/slovnik.js"></script>')
    (SLOVNIK / "index.html").write_text(page, encoding="utf-8")
    return shown


# ---------- stránka pojmu ----------

def parse_obsah(slug):
    raw = (SLOVNIK / "_obsah" / f"{slug}.html").read_text(encoding="utf-8")
    m = re.match(r"\s*<!--(.*?)-->", raw, re.S)
    meta, faq = {}, []
    infaq = False
    for line in m.group(1).strip().splitlines():
        if line.startswith("faq:"):
            infaq = True
            continue
        if infaq and line.startswith("- "):
            q, a = line[2:].split("|", 1)
            faq.append((q.strip(), a.strip()))
            continue
        k, _, v = line.partition(":")
        meta[k.strip()] = v.strip()
    return meta, faq, raw[m.end():].strip()


def build_term(p, kat, pojmy, by_slug):
    meta, faq, content = parse_obsah(p["slug"])
    url = f'{BASE}/slovnik/{p["slug"]}'
    upd = meta.get("aktualizovano", str(date.today()))
    d = date.fromisoformat(upd)
    upd_cs = f"{d.day}. {d.month}. {d.year}"

    soup = BeautifulSoup(content, "lxml")
    toc = [(h.get("id"), h.get_text(" ", strip=True)) for h in soup.find_all("h2") if h.get("id")]
    if faq:
        toc.append(("faq", "Časté otázky"))
    toc_html = "".join(f'<li><a href="#{i}">{esc(t)}</a></li>' for i, t in toc)

    def live(x):
        return x["stav"] in ("hotovo", "clanek") or (INCLUDE_DRAFT and x["priorita"] == 1)
    rel = [by_slug[s.strip()] for s in meta.get("souvisejici", "").split(",") if s.strip() in by_slug and live(by_slug[s.strip()])]
    # odkazy v textu na pojmy bez stránky převést na prostý text
    def unlink(m):
        t = by_slug.get(m.group(1))
        return m.group(0) if (t is None or live(t)) else m.group(2)
    content = re.sub(r'<a href="([a-z0-9-]+)">(.*?)</a>', unlink, content)
    rel_html = "".join(f'<a class="slovnik-rel" href="{esc(term_href(r))}">{esc(r["pojem"])}</a>' for r in rel)

    art = article_info(p["clanky"][0]) if p.get("clanky") else None
    art_html = ""
    if art:
        art_html = f'''<a class="card slovnik-side-article hover-transform-1-01" href="../blog/{art["slug"]}">
<img src="{esc(art["img"])}" alt="" loading="lazy"/>
<div class="slovnik-side-article__body"><div class="slovnik-side__label">Do hloubky v článku</div>
<p class="slovnik-side-article__title">{esc(art["title"])}</p>
<div class="text-200 bold color-neutral-800"><span class="link-text">Číst článek</span><span class="line-rounded-icon link-icon-right"></span></div></div></a>'''

    faq_html = ""
    if faq:
        items = "".join(f'<details class="slovnik-faq__item"><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q, a in faq)
        faq_html = f'<section class="slovnik-faq" id="faq"><h2 class="seo-from-h2 slovnik-faq__title">Časté otázky</h2>{items}</section>'

    ordered = sorted([x for x in pojmy if x["stav"] == "hotovo" or (INCLUDE_DRAFT and x["priorita"] == 1)],
                     key=lambda x: sort_key(x["pojem"]))
    i = next(k for k, x in enumerate(ordered) if x["slug"] == p["slug"])
    prev, nxt = ordered[i - 1] if i > 0 else None, ordered[i + 1] if i + 1 < len(ordered) else None
    pn = '<nav class="slovnik-pn" aria-label="Předchozí a další pojem">'
    pn += (f'<a class="card slovnik-pn__link" href="{esc(term_href(prev))}"><span class="slovnik-pn__dir">← Předchozí pojem</span>'
           f'<span class="slovnik-pn__term">{esc(prev["pojem"])}</span></a>') if prev else "<span></span>"
    pn += '<a class="slovnik-pn__all" href="./">Všechny pojmy A–Ž</a>'
    pn += (f'<a class="card slovnik-pn__link is-next" href="{esc(term_href(nxt))}"><span class="slovnik-pn__dir">Další pojem →</span>'
           f'<span class="slovnik-pn__term">{esc(nxt["pojem"])}</span></a>') if nxt else "<span></span>"
    pn += "</nav>"

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": meta["title"], "description": meta["description"],
         "inLanguage": "cs", "isPartOf": {"@id": f"{BASE}/#website"}, "author": PERSON, "dateModified": upd,
         "mainEntity": {"@id": url + "#term"}},
        {"@type": "DefinedTerm", "@id": url + "#term", "name": full_label(p), "description": p["definice"],
         "url": url, "inDefinedTermSet": {"@id": f"{BASE}/slovnik/#set"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Úvod", "item": BASE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Slovník pojmů", "item": BASE + "/slovnik/"},
            {"@type": "ListItem", "position": 3, "name": p["pojem"], "item": url}]}]}
    if faq:
        schema["@graph"].append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]})

    k = kat[p["kategorie"]]
    body = f'''<div class="top-section pd-top-56px bg-secondary-5 slovnik-hero">
<div class="container-default position-relative---z-index-1 w-container">
<nav class="slovnik-breadcrumb" aria-label="Drobečková navigace"><a href="../">Úvod</a><span>/</span><a href="./">Slovník pojmů</a><span>/</span><span aria-current="page">{esc(p["pojem"])}</span></nav>
<div class="flex-horizontal gap-column-16px mg-bottom-16px">
<span class="badge-secondary slovnik-badge" style="--chip:{k["barva"]}"><span class="slovnik-chip__dot"></span>{esc(k["nazev"])}</span>
<div class="text-200 semi-bold">Aktualizováno {upd_cs}</div>
</div>
<div class="text-center">
<div class="inner-container _966px center"><h1 class="display-2 mg-bottom-16px">{esc(meta["h1"])}</h1></div>
<div class="inner-container _686px center"><p class="mg-bottom-0">{esc(meta["perex"])}</p></div>
</div>
</div>
{dots()}
</div>

<div class="section pd-top-64px pd-bottom-100px">
<div class="container-default w-container">
<div class="grid-2-columns _2-06fr---1fr slovnik-layout">
<article class="slovnik-article">
{content}
{faq_html}
<div class="card slovnik-author">
<img src="../assets/images/foto-toonja.jpg" alt="Marek Turnhöfer" loading="lazy"/>
<div><p class="slovnik-author__name">Marek Turnhöfer</p>
<p class="mg-bottom-0">Online marketingový konzultant. Přes 10 let dělám marketing e-shopům a startupům a weby si stavím s AI. Ve slovníku vysvětluju pojmy, se kterými denně pracuju.</p></div>
</div>
</article>
<aside class="slovnik-side">
<div class="card slovnik-side__box"><div class="slovnik-side__label">Na stránce</div><ol class="slovnik-toc">{toc_html}</ol></div>
<div class="card slovnik-side__box"><div class="slovnik-side__label">Související pojmy</div><div class="slovnik-rels">{rel_html}</div></div>
{art_html}
<div class="card newsletter-sticky-card slovnik-side__cta">
<p class="color-neutral-100 seo-from-h3">Chcete to nasadit u sebe?</p>
<p class="mg-bottom-24px">Projdeme váš web a řeknu vám na rovinu, co se vyplatí.</p>
<a class="btn-primary white w-button" href="../contact">Napište mi</a>
<div class="bg-dot newsletter-card---top-right-dot"></div><div class="bg-dot newsletter-card---bottom-left-dot"></div>
</div>
</aside>
</div>
{pn}
</div>
</div>
'''
    page = head(meta["title"], meta["description"], url, schema, "article") + body + foot()
    (SLOVNIK / f'{p["slug"]}.html').write_text(page, encoding="utf-8")


def update_sitemap(pojmy):
    f = ROOT / "sitemap.xml"
    s = f.read_text(encoding="utf-8")
    s = re.sub(r"\s*<url><loc>https://www\.toonja\.cz/slovnik/[^<]*</loc>.*?</url>", "", s)
    today = str(date.today())
    rows = [f"  <url><loc>{BASE}/slovnik/</loc><lastmod>{today}</lastmod></url>"]
    for p in sorted(pojmy, key=lambda x: sort_key(x["pojem"])):
        if p["stav"] == "hotovo":
            meta, _, _ = parse_obsah(p["slug"])
            rows.append(f'  <url><loc>{BASE}/slovnik/{p["slug"]}</loc><lastmod>{meta.get("aktualizovano", today)}</lastmod></url>')
    s = s.replace("</urlset>", "\n".join(rows) + "\n</urlset>")
    f.write_text(s, encoding="utf-8")


def update_llms(pojmy):
    """Přepíše sekci „## Slovník pojmů“ v llms.txt podle hotových pojmů."""
    f = ROOT / "llms.txt"
    if not f.exists():
        return
    rows = ["## Slovník pojmů", "",
            f"- [Slovník pojmů online marketingu]({BASE}/slovnik/): Rozcestník všech pojmů od A do Ž."]
    for p in sorted(pojmy, key=lambda x: sort_key(x["pojem"])):
        if p["stav"] == "hotovo":
            rows.append(f'- [{full_label(p)}]({BASE}/slovnik/{p["slug"]}): {p["definice"]}')
    s = re.sub(r"## Slovník pojmů\n.*?(?=\n## )", "\n".join(rows) + "\n", f.read_text(encoding="utf-8"), flags=re.S)
    f.write_text(s, encoding="utf-8")


# ---------- kontrola článků ----------

def check(include_all):
    kat, pojmy = load()
    pool = [p for p in pojmy if (include_all or p["stav"] in ("hotovo", "clanek")) and p.get("tvary")]
    found = 0
    for f in sorted((ROOT / "blog").glob("*.html")):
        if f.name == "index.html":
            continue
        soup = BeautifulSoup(f.read_text(encoding="utf-8"), "lxml")
        rt = soup.select_one(".rich-text")
        if not rt:
            continue
        linked = {a.get("href", "").rstrip("/").split("/")[-1] for a in rt.find_all("a")}
        print(f"\n== blog/{f.name}")
        n = 0
        for p in pool:
            target = p.get("url", p["slug"]).split("/")[-1]
            if target in linked or target == f.stem:
                continue
            hit = None
            for el in rt.find_all(["p", "li"]):
                if el.find_parent(["h1", "h2", "h3", "h4"]):
                    continue
                txt = " ".join(t for t in el.find_all(string=True) if not t.find_parent("a"))
                for form in p["tvary"]:
                    flags = 0 if form.isupper() else re.I
                    m = re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", txt, flags)
                    if m:
                        a, b = max(0, m.start() - 50), min(len(txt), m.end() + 50)
                        hit = (m.group(0), txt[a:b].strip())
                        break
                if hit:
                    break
            if hit:
                n += 1
                found += 1
                stav = "" if p["stav"] != "navrh" else "  [stránka zatím neexistuje]"
                print(f'  + {p["pojem"]} -> /slovnik/{p["slug"]}{stav}\n      „…{hit[1]}…“')
        if not n:
            print("  vše prolinkováno")
    print(f"\nNávrhů odkazů: {found}. Pravidla: první výskyt v textu, ne v nadpisu, max 5 pojmů na článek.")


# ---------- main ----------

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "build"
    INCLUDE_DRAFT = "--navrh" in sys.argv
    if cmd == "check":
        check("--vse" in sys.argv)
        sys.exit(0)
    PARTS = site_parts()
    kat, pojmy = load()
    by_slug = {p["slug"]: p for p in pojmy}
    shown = build_hub(kat, pojmy, INCLUDE_DRAFT)
    built = 0
    for p in pojmy:
        if (SLOVNIK / "_obsah" / f'{p["slug"]}.html').exists():
            build_term(p, kat, pojmy, by_slug)
            built += 1
    if not INCLUDE_DRAFT:
        update_sitemap(pojmy)
        update_llms(pojmy)
    print(f"Rozcestník: {len(shown)} pojmů. Stránek pojmů: {built}." + ("" if INCLUDE_DRAFT else " Sitemap a llms.txt aktualizovány."))
