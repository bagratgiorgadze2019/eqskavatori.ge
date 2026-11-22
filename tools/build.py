# -*- coding: utf-8 -*-
"""Build eqskavatori.ge (static, GitHub Pages).

URLs:  /  (Georgian home, x-default)   /en/  /ru/   /{ka,en,ru}/<slug>/   /ka/ -> redirect to /
Writes every page + index.md / index.html.md (AI copies) + sitemap.xml + robots.txt + llms.txt + llms-full.txt + 404.html.
Run:  npm run build   (= python3 tools/build.py && tailwind && python3 tools/build.py stamp)
Idempotent. Content lives in tools/content.py.
"""
import json
import re
import sys
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content import BRAND, EMAIL, GUIDE, HOME, PHONE, PHONE_FMT, S, UI, WA  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://eqskavatori.ge"
LANGS = ("ka", "en", "ru")
LOCALE = {"ka": "ka_GE", "en": "en_US", "ru": "ru_RU"}
LANG_SHORT = {"ka": "ქა", "en": "EN", "ru": "RU"}
LANG_NAME = {"ka": "ქართული", "en": "English", "ru": "Русский"}
BIZ_ID = f"{SITE}/#business"
TODAY = date.today().isoformat()
INDEXNOW_KEY = "82c7b423b13d3f83807f817236c9210d"

ICON = lambda d, cls="h-6 w-6": f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{d}</svg>'
PHONE_SVG = ICON('<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.3 1.8.6 2.6a2 2 0 0 1-.5 2.1L8 9.6a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.8.3 1.7.5 2.6.6a2 2 0 0 1 1.7 2Z"/>', "h-5 w-5 shrink-0")
WA_SVG = '<svg class="h-5 w-5 shrink-0" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2a10 10 0 0 0-8.5 15.2L2 22l4.9-1.3A10 10 0 1 0 12 2Zm5.3 14.1c-.2.6-1.3 1.2-1.8 1.2-.5.1-1 .1-1.7-.1-.4-.1-.9-.3-1.6-.6-2.8-1.2-4.6-4-4.7-4.2-.1-.2-1.1-1.5-1.1-2.8s.7-2 .9-2.2c.2-.2.5-.3.7-.3h.5c.2 0 .4 0 .6.5l.8 1.9c.1.2.1.3 0 .5l-.4.6c-.2.2-.3.4-.1.7.2.3.8 1.3 1.7 2.1 1.2 1 2.1 1.4 2.4 1.5.2.1.4.1.6-.1l.7-.9c.2-.2.4-.2.6-.1l1.8.9c.3.1.4.2.5.3.1.2.1.6-.1 1.1Z"/></svg>'
CHECK = ICON('<path d="M20 6 9 17l-5-5"/>', "mt-0.5 h-5 w-5 shrink-0 text-brand-300")
MAIL_SVG = ICON('<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>', "h-5 w-5 shrink-0")
PIN_SVG = ICON('<path d="M12 21s7-6.2 7-11a7 7 0 0 0-14 0c0 4.8 7 11 7 11Z"/><circle cx="12" cy="10" r="2.5"/>', "h-5 w-5 shrink-0")


# ------------------------------------------------------------------ URLs
def home_url(lang):
    return "/" if lang == "ka" else f"/{lang}/"


def svc_url(s, lang):
    return f"/{lang}/{s['slug'][lang]}/"


def out_file(url):
    return ROOT / url.strip("/") / "index.html" if url != "/" else ROOT / "index.html"


def wa_link(lang, topic):
    return f"https://wa.me/{WA}?text=" + quote(UI[lang]["wa_text"].format(x=topic))


def faq_items(lang, faq):
    U = UI[lang]
    return [U["faq_bobcat"] if f == ("bobcat",) else f for f in faq]


# ------------------------------------------------------------------ shared chrome
def header(lang, urls):
    U = UI[lang]
    pills = "".join(
        f'<a href="{urls[l]}" hreflang="{l}" lang="{l}" class="grid h-9 min-w-9 place-items-center rounded-md px-2 text-xs font-bold '
        + ('bg-brand text-white" aria-current="true"' if l == lang else 'text-zinc-300 hover:bg-zinc-800"')
        + f' title="{LANG_NAME[l]}">{LANG_SHORT[l]}</a>' for l in LANGS)
    home = home_url(lang)
    links = [(f"{home}#services", U["services"]), (f"/{lang}/{GUIDE['slug'][lang]}/", U["guide"]), ("#contact", U["contact"])]
    nav = "".join(f'<a href="{h}" class="hover:text-white">{t}</a>' for h, t in links)
    mnav = "".join(f'<a href="{h}" class="block rounded-lg px-3 py-3 text-base hover:bg-zinc-900">{t}</a>' for h, t in links)
    return f'''<header class="sticky top-0 z-40 border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur">
  <div class="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-2.5">
    <a href="{home}" class="flex min-w-0 items-center gap-2" aria-label="{BRAND} — {U['home']}">
      <img src="/assets/favicon.svg" width="36" height="36" alt="" class="h-9 w-9 shrink-0">
      <span class="truncate font-head text-lg font-extrabold tracking-tight text-white">Eqskavatori<span class="text-brand-300">.ge</span></span>
    </a>
    <nav class="hidden items-center gap-6 text-sm text-zinc-300 md:flex" aria-label="{U['menu']}">{nav}</nav>
    <div class="flex items-center gap-2">
      <nav class="flex items-center gap-0.5 rounded-lg bg-zinc-900 p-0.5 ring-1 ring-zinc-800" aria-label="{U['lang_label']}">{pills}</nav>
      <a href="tel:{PHONE}" class="hidden items-center gap-2 rounded-lg bg-brand px-4 py-2 text-sm font-bold text-white hover:bg-brand-600 lg:inline-flex">{PHONE_SVG}{PHONE_FMT}</a>
      <button id="navBtn" type="button" aria-label="{U['menu']}" aria-expanded="false" aria-controls="navMenu" class="grid h-10 w-10 place-items-center rounded-lg bg-zinc-900 ring-1 ring-zinc-800 md:hidden">{ICON('<path d="M4 7h16M4 12h16M4 17h16"/>', "h-5 w-5")}</button>
    </div>
  </div>
  <nav id="navMenu" class="hidden border-t border-zinc-800 px-4 py-2 text-zinc-200 md:hidden" aria-label="{U['menu']}">{mnav}</nav>
</header>'''


def footer(lang, urls):
    U = UI[lang]
    svc_links = "".join(f'<li><a href="{svc_url(s, lang)}" class="hover:text-white">{escape(s[lang]["h1"])}</a></li>' for s in S[:7])
    langs = " · ".join(f'<a href="{urls[l]}" hreflang="{l}" lang="{l}" class="hover:text-white">{LANG_NAME[l]}</a>' for l in LANGS)
    return f'''<footer class="border-t border-zinc-800 bg-zinc-950 pb-24 md:pb-0">
  <div class="mx-auto grid max-w-6xl gap-8 px-4 py-12 sm:grid-cols-2 lg:grid-cols-3">
    <div>
      <div class="flex items-center gap-2"><img src="/assets/favicon.svg" width="32" height="32" alt="" class="h-8 w-8"><span class="font-head text-lg font-extrabold text-white">Eqskavatori<span class="text-brand-300">.ge</span></span></div>
      <p class="mt-3 text-sm text-zinc-400">{U['footer']}</p>
      <p class="mt-4 text-sm"><a href="tel:{PHONE}" class="font-semibold text-white">{PHONE_FMT}</a> · <a href="mailto:{EMAIL}" class="text-zinc-300">{EMAIL}</a></p>
    </div>
    <div>
      <h2 class="text-sm font-semibold text-zinc-200">{U['services']}</h2>
      <ul class="mt-3 space-y-2 text-sm text-zinc-400">{svc_links}<li><a href="{home_url(lang)}#services" class="font-semibold text-brand-300 hover:text-white">{U['all_services']} →</a></li></ul>
    </div>
    <div>
      <h2 class="text-sm font-semibold text-zinc-200">{U['lang_label']}</h2>
      <p class="mt-3 text-sm text-zinc-400">{langs}</p>
    </div>
  </div>
  <p class="border-t border-zinc-800/70 py-5 text-center text-xs text-zinc-400">© 2026 {BRAND}</p>
</footer>'''


def mobile_bar(lang, topic):
    U = UI[lang]
    return f'''<div class="fixed inset-x-0 bottom-0 z-50 grid grid-cols-2 gap-2 border-t border-zinc-800 bg-zinc-950/95 p-2 backdrop-blur md:hidden" style="padding-bottom:max(.5rem,env(safe-area-inset-bottom))">
  <a href="tel:{PHONE}" class="flex h-12 items-center justify-center gap-2 rounded-xl bg-brand font-bold text-white">{PHONE_SVG}{U['call']}</a>
  <a href="{wa_link(lang, topic)}" class="flex h-12 items-center justify-center gap-2 rounded-xl bg-[#15803d] font-bold text-white">{WA_SVG}WhatsApp</a>
</div>'''


def cta_buttons(lang, topic):
    U = UI[lang]
    return (f'<div class="mt-7 flex flex-col gap-3 sm:flex-row">'
            f'<a href="tel:{PHONE}" class="flex h-13 items-center justify-center gap-2 rounded-xl bg-brand px-6 py-3.5 text-lg font-bold text-white hover:bg-brand-600">{PHONE_SVG}{U["call"]} {PHONE_FMT}</a>'
            f'<a href="{wa_link(lang, topic)}" class="flex h-13 items-center justify-center gap-2 rounded-xl bg-[#15803d] px-6 py-3.5 text-lg font-bold text-white">{WA_SVG}WhatsApp</a></div>')


def picture(alt, eager=False, cls="h-full w-full object-cover"):
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    return (f'<picture><source type="image/avif" srcset="/assets/excavator-450.avif 450w, /assets/excavator-900.avif 900w" sizes="(min-width:1024px) 420px, 100vw">'
            f'<source type="image/webp" srcset="/assets/excavator-450.webp 450w, /assets/excavator-900.webp 900w" sizes="(min-width:1024px) 420px, 100vw">'
            f'<img src="/assets/excavator-900.jpg" width="900" height="1100" alt="{escape(alt)}" {load} decoding="async" class="{cls}"></picture>')


def faq_html(items):
    return '<div class="mt-5 space-y-3">' + "".join(
        f'<details class="group rounded-2xl bg-zinc-900 ring-1 ring-zinc-800 open:ring-brand/40"><summary class="flex min-h-12 cursor-pointer list-none items-center justify-between gap-4 p-5 font-semibold">'
        f'<span>{escape(q)}</span><span class="text-xl text-brand-300 transition group-open:rotate-45" aria-hidden="true">+</span></summary>'
        f'<p class="-mt-1 px-5 pb-5 text-zinc-300">{escape(a)}</p></details>' for q, a in items) + "</div>"


def ul(items):
    return '<ul class="mt-5 grid gap-3 sm:grid-cols-2">' + "".join(
        f'<li class="flex gap-3 rounded-xl bg-zinc-900 p-4 ring-1 ring-zinc-800">{CHECK}<span>{escape(x)}</span></li>' for x in items) + "</ul>"


def contact_section(lang, topic):
    U = UI[lang]
    return f'''<section id="contact" class="border-t border-zinc-800 bg-zinc-900/40">
  <div class="mx-auto max-w-6xl px-4 py-14">
    <h2 class="font-head text-3xl font-extrabold">{U['contact_h']}</h2>
    <p class="mt-3 max-w-2xl text-zinc-300">{U['contact_p']}</p>
    <div class="mt-8 grid gap-3 sm:grid-cols-3">
      <a href="tel:{PHONE}" class="flex items-center gap-3 rounded-2xl bg-zinc-950 p-5 ring-1 ring-zinc-800 hover:ring-brand/60"><span class="text-brand-300">{PHONE_SVG}</span><span><span class="block text-sm text-zinc-400">{U['phone']}</span><span class="font-bold">{PHONE_FMT}</span></span></a>
      <a href="mailto:{EMAIL}" class="flex items-center gap-3 rounded-2xl bg-zinc-950 p-5 ring-1 ring-zinc-800 hover:ring-brand/60"><span class="text-brand-300">{MAIL_SVG}</span><span><span class="block text-sm text-zinc-400">{U['email']}</span><span class="font-bold">{EMAIL}</span></span></a>
      <div class="flex items-center gap-3 rounded-2xl bg-zinc-950 p-5 ring-1 ring-zinc-800"><span class="text-brand-300">{PIN_SVG}</span><span><span class="block text-sm text-zinc-400">{U['area']}</span><span class="font-bold">{U['area_v']}</span></span></div>
    </div>
    {cta_buttons(lang, topic)}
  </div>
</section>'''


def business_ld(lang):
    return {"@type": "HomeAndConstructionBusiness", "@id": BIZ_ID, "name": BRAND, "url": SITE + "/", "telephone": PHONE, "email": EMAIL,
            "image": f"{SITE}/assets/og.jpg", "logo": f"{SITE}/assets/icon-512.png", "description": HOME[lang]["desc"].split(" ☎")[0],
            "address": {"@type": "PostalAddress", "addressLocality": "Tbilisi", "addressCountry": "GE"},
            "areaServed": {"@type": "City", "name": "Tbilisi"}, "knowsLanguage": list(LANGS),
            "contactPoint": {"@type": "ContactPoint", "telephone": PHONE, "contactType": "customer service", "availableLanguage": ["Georgian", "English", "Russian"]}}


def page(lang, url, urls, title, desc, kw, schema, body, topic, og_type="website"):
    md = url + "index.md" if url.endswith("/") else url + ".md"
    alts = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{urls[l]}">' for l in LANGS) + f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{urls["ka"]}">'
    loc_alts = "\n".join(f'<meta property="og:locale:alternate" content="{LOCALE[l]}">' for l in LANGS if l != lang)
    ld = json.dumps({"@context": "https://schema.org", "@graph": schema}, ensure_ascii=False, indent=1)
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<meta name="keywords" content="{escape(kw)}">
<meta name="robots" content="index, follow, max-image-preview:large">
<link rel="canonical" href="{SITE}{url}">
{alts}
<link rel="alternate" type="text/markdown" href="{SITE}{md}">
<meta name="theme-color" content="#09090b">
<meta name="geo.region" content="GE-TB"><meta name="geo.placename" content="Tbilisi">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:url" content="{SITE}{url}">
<meta property="og:image" content="{SITE}/assets/og.jpg">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:locale" content="{LOCALE[lang]}">
{loc_alts}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{escape(title)}">
<meta name="twitter:description" content="{escape(desc)}">
<meta name="twitter:image" content="{SITE}/assets/og.jpg">
<link rel="icon" href="/favicon.ico" sizes="32x32">
<link rel="icon" href="/assets/favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<link rel="manifest" href="/site.webmanifest">
<link rel="preload" href="/assets/fonts/noto-sans-georgian-800-georgian.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/styles.css">
<script type="application/ld+json">
{ld}
</script>
</head>
<body class="bg-zinc-950 font-sans text-zinc-100 antialiased">
<a href="#main" class="sr-only focus:not-sr-only focus:fixed focus:left-2 focus:top-2 focus:z-50 focus:rounded focus:bg-brand focus:px-3 focus:py-2 focus:text-white">↓</a>
{header(lang, urls)}
<main id="main">
{body}
</main>
{footer(lang, urls)}
{mobile_bar(lang, topic)}
<script>
  (function () {{ var b = document.getElementById("navBtn"), m = document.getElementById("navMenu");
    b.addEventListener("click", function () {{ var o = m.classList.toggle("hidden"); b.setAttribute("aria-expanded", String(!o)); }}); }})();
</script>
</body>
</html>
'''


def crumbs_ld(items):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in items]}


def breadcrumb_html(items):
    parts = []
    for i, (n, u) in enumerate(items):
        parts.append(f'<span aria-current="page" class="text-zinc-200">{escape(n)}</span>' if i == len(items) - 1 else f'<a href="{u}" class="hover:text-white">{escape(n)}</a>')
    return '<nav aria-label="breadcrumb" class="mb-4 text-sm text-zinc-400">' + ' <span aria-hidden="true">/</span> '.join(parts) + "</nav>"


def service_card(s, lang, featured=False):
    d = s[lang]
    span = " sm:col-span-2 lg:col-span-3 bg-gradient-to-r from-brand/25 to-zinc-900 ring-brand/40" if featured else " bg-zinc-900 ring-zinc-800"
    return (f'<a href="{svc_url(s, lang)}" class="group flex items-start gap-4 rounded-2xl p-5 ring-1 transition hover:ring-brand-300/60{span}">'
            f'<span class="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-brand-300/10 text-brand-300 ring-1 ring-brand-300/25">{ICON(s["icon"])}</span>'
            f'<span class="min-w-0"><span class="block font-head text-lg font-bold leading-snug text-white group-hover:text-brand-300">{escape(d["h1"])}</span>'
            f'<span class="mt-1 block text-sm text-zinc-400">{escape(d["card"])}</span></span></a>')


# ------------------------------------------------------------------ pages
def build_home(lang):
    U, H = UI[lang], HOME[lang]
    urls = {l: home_url(l) for l in LANGS}
    faq = [U["faq_price"], U["faq_operator"], U["faq_bobcat"], U["faq_area"]]
    steps = "".join(f'<li class="rounded-2xl bg-zinc-900 p-5 ring-1 ring-zinc-800"><span class="grid h-9 w-9 place-items-center rounded-full bg-brand font-bold text-white">{i + 1}</span>'
                    f'<h3 class="mt-3 font-semibold">{escape(t)}</h3><p class="mt-1 text-sm text-zinc-400">{escape(p)}</p></li>' for i, (t, p) in enumerate(U["steps"]))
    why = "".join(f'<li class="rounded-2xl bg-zinc-900 p-5 ring-1 ring-zinc-800"><h3 class="font-semibold text-brand-300">{escape(t)}</h3><p class="mt-1 text-sm text-zinc-300">{escape(p)}</p></li>' for t, p in U["why"])
    guide = f"/{lang}/{GUIDE['slug'][lang]}/"
    body = f'''<section class="mx-auto grid max-w-6xl gap-8 px-4 pb-12 pt-6 lg:grid-cols-[1fr_420px] lg:items-center lg:pt-12">
  <div>
    <p class="inline-flex rounded-full bg-brand-300/10 px-3 py-1 text-xs font-semibold text-brand-300 ring-1 ring-brand-300/25">{escape(H['kicker'])}</p>
    <h1 class="mt-4 font-head text-4xl font-extrabold leading-tight sm:text-5xl">{escape(H['h1'])}</h1>
    <p class="mt-4 text-lg leading-relaxed text-zinc-300">{escape(H['lead'])}</p>
    {cta_buttons(lang, H['h1'])}
  </div>
  <div class="relative aspect-[9/11] overflow-hidden rounded-3xl ring-1 ring-zinc-800 max-lg:max-h-[70vh] max-lg:aspect-[4/5]">{picture(H['photo_alt'], eager=True)}</div>
</section>

<section id="services" class="mx-auto max-w-6xl scroll-mt-20 px-4 py-12">
  <h2 class="font-head text-3xl font-extrabold">{escape(H['services_h'])}</h2>
  <p class="mt-2 text-zinc-400">{escape(H['services_p'])}</p>
  <div class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{service_card(S[0], lang, featured=True)}{"".join(service_card(s, lang) for s in S[1:])}</div>
  <p class="mt-6 text-zinc-300">{escape(H['synonyms'])} <a href="{guide}" class="font-semibold text-brand-300">{escape(H['guide_cta'])}</a></p>
</section>

<section class="mx-auto max-w-6xl px-4 py-12">
  <h2 class="font-head text-3xl font-extrabold">{U['how_h']}</h2>
  <ol class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{steps}</ol>
</section>

<section class="mx-auto max-w-6xl px-4 py-12">
  <h2 class="font-head text-3xl font-extrabold">{U['why_h']}</h2>
  <ul class="mt-8 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">{why}</ul>
</section>

<section class="mx-auto max-w-3xl px-4 py-12">
  <h2 class="font-head text-3xl font-extrabold">{U['faq']}</h2>
  {faq_html(faq)}
</section>
{contact_section(lang, H['h1'])}'''
    schema = [business_ld(lang) | {"hasOfferCatalog": {"@type": "OfferCatalog", "name": U["services"], "itemListElement": [
                  {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s[lang]["h1"], "url": SITE + svc_url(s, lang)}} for s in S]}},
              {"@type": "WebSite", "@id": f"{SITE}/#website", "url": SITE + "/", "name": BRAND, "inLanguage": lang, "publisher": {"@id": BIZ_ID}},
              faq_ld(faq)]
    write(home_url(lang), page(lang, home_url(lang), urls, H["title"], H["desc"], H["kw"], schema, body, H["h1"]))
    return dict(url=home_url(lang), title=H["title"], h1=H["h1"], lead=H["lead"], sections=[(H["services_h"], [f"[{s[lang]['h1']}]({SITE}{svc_url(s, lang)}) — {s[lang]['card']}" for s in S]),
                (U["how_h"], [f"{t} — {p}" for t, p in U["steps"]]), (U["why_h"], [f"{t} — {p}" for t, p in U["why"]])], faq=faq)


def build_service(s, lang):
    U, d = UI[lang], s[lang]
    urls = {l: svc_url(s, l) for l in LANGS}
    faq = faq_items(lang, d["faq"]) + [U["faq_price"], U["faq_operator"]]
    crumbs = [(U["home"], home_url(lang)), (U["services"], home_url(lang) + "#services"), (d["h1"], urls[lang])]
    related = [x for x in S if x is not s][:6] if s["key"] == "hire" else [S[0]] + [x for x in S[1:] if x is not s][:5]
    secs = "".join(f'<h2 class="mt-10 font-head text-2xl font-bold">{escape(h)}</h2><p class="mt-3 leading-relaxed text-zinc-300">{escape(p)}</p>' for h, p in d["sec"])
    guide = f"/{lang}/{GUIDE['slug'][lang]}/"
    body = f'''<section class="mx-auto grid max-w-6xl gap-8 px-4 pb-10 pt-6 lg:grid-cols-[1fr_360px] lg:pt-10">
  <div>
    {breadcrumb_html(crumbs)}
    <p class="inline-flex items-center gap-2 rounded-full bg-brand-300/10 px-3 py-1 text-xs font-semibold text-brand-300 ring-1 ring-brand-300/25"><span>{ICON(s['icon'], 'h-4 w-4')}</span>{U['operator_badge']}</p>
    <h1 class="mt-4 font-head text-3xl font-extrabold leading-tight sm:text-5xl">{escape(d['h1'])}</h1>
    <p class="mt-4 text-lg leading-relaxed text-zinc-300">{escape(d['lead'])}</p>
    {cta_buttons(lang, d['h1'])}
  </div>
  <div class="relative hidden aspect-[9/11] overflow-hidden rounded-3xl ring-1 ring-zinc-800 lg:block">{picture(HOME[lang]['photo_alt'])}</div>
</section>

<section class="mx-auto max-w-6xl px-4 pb-12">
  <div class="max-w-3xl">
    <h2 class="font-head text-2xl font-bold">{U['inc']}</h2>
    {ul(d['inc'])}
    <h2 class="mt-10 font-head text-2xl font-bold">{U['uses']}</h2>
    {ul(d['uses'])}
    {secs}
    <h2 class="mt-10 font-head text-2xl font-bold">{U['faq']}</h2>
    {faq_html(faq)}
    <p class="mt-8"><a href="{guide}" class="font-semibold text-brand-300">{escape(HOME[lang]['guide_cta'])}</a></p>
  </div>
  <h2 class="mt-12 font-head text-2xl font-bold">{U['related']}</h2>
  <div class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">{"".join(service_card(x, lang) for x in related)}</div>
</section>
{contact_section(lang, d['h1'])}'''
    service = {"@type": "Service", "@id": SITE + urls[lang] + "#service", "name": d["h1"], "serviceType": d["h1"], "description": d["desc"].split(" ☎")[0],
               "url": SITE + urls[lang], "provider": {"@id": BIZ_ID}, "areaServed": {"@type": "City", "name": "Tbilisi"}, "inLanguage": lang}
    schema = [business_ld(lang), service, faq_ld(faq), crumbs_ld(crumbs[::2])]
    write(urls[lang], page(lang, urls[lang], urls, d["title"], d["desc"], d["kw"], schema, body, d["h1"]))
    return dict(url=urls[lang], title=d["title"], h1=d["h1"], lead=d["lead"], sections=[(U["inc"], d["inc"]), (U["uses"], d["uses"])] + [(h, [p]) for h, p in d["sec"]], faq=faq)


def build_guide(lang):
    U, g = UI[lang], GUIDE[lang]
    urls = {l: f"/{l}/{GUIDE['slug'][l]}/" for l in LANGS}
    faq = faq_items(lang, g["faq"])
    crumbs = [(U["home"], home_url(lang)), (g["h1"], urls[lang])]
    jobs = [x for x in S if x["key"] != "hire"]
    items = "".join(f'<li class="rounded-2xl bg-zinc-900 p-5 ring-1 ring-zinc-800"><h3 class="font-head text-lg font-bold"><span class="text-brand-300">{i + 1}.</span> '
                    f'<a href="{svc_url(x, lang)}" class="hover:text-brand-300">{escape(x[lang]["h1"])}</a></h3><p class="mt-1 text-zinc-300">{escape(x[lang]["card"])}</p></li>'
                    for i, x in enumerate(jobs))
    body = f'''<article class="mx-auto max-w-3xl px-4 pb-12 pt-6 lg:pt-10">
  {breadcrumb_html(crumbs)}
  <h1 class="font-head text-3xl font-extrabold leading-tight sm:text-5xl">{escape(g['h1'])}</h1>
  <p class="mt-4 text-lg leading-relaxed text-zinc-300">{escape(g['intro'])}</p>
  <h2 class="mt-10 font-head text-2xl font-bold">{escape(g['list_h'])}</h2>
  <ol class="mt-5 space-y-3">{items}</ol>
  <h2 class="mt-10 font-head text-2xl font-bold">{escape(g['compare_h'])}</h2>
  <p class="mt-3 leading-relaxed text-zinc-300">{escape(g['compare'])}</p>
  <h2 class="mt-10 font-head text-2xl font-bold">{escape(g['when_h'])}</h2>
  {ul(g['when'])}
  <h2 class="mt-10 font-head text-2xl font-bold">{U['faq']}</h2>
  {faq_html(faq)}
  <p class="mt-8"><a href="{svc_url(S[0], lang)}" class="font-semibold text-brand-300">{escape(S[0][lang]['h1'])} →</a></p>
</article>
{contact_section(lang, g['h1'])}'''
    article = {"@type": "Article", "headline": g["h1"], "description": g["desc"], "inLanguage": lang, "image": [f"{SITE}/assets/og.jpg"],
               "datePublished": "2026-11-22", "dateModified": "2026-11-22", "mainEntityOfPage": SITE + urls[lang],
               "author": {"@id": BIZ_ID}, "publisher": {"@id": BIZ_ID}}
    schema = [business_ld(lang), article, faq_ld(faq), crumbs_ld(crumbs)]
    write(urls[lang], page(lang, urls[lang], urls, g["title"], g["desc"], g["kw"], schema, body, g["h1"], og_type="article"))
    return dict(url=urls[lang], title=g["title"], h1=g["h1"], lead=g["intro"],
                sections=[(g["list_h"], [f"[{x[lang]['h1']}]({SITE}{svc_url(x, lang)}) — {x[lang]['card']}" for x in jobs]),
                          (g["compare_h"], [g["compare"]]), (g["when_h"], g["when"])], faq=faq)


def write(url, html):
    p = out_file(url)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(html, encoding="utf-8")


def stub(path, target, title="Redirect"):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(f'<!DOCTYPE html>\n<html><head><meta charset="utf-8"><title>{title}</title><link rel="canonical" href="{SITE}{target}">'
                 f'<meta name="robots" content="noindex, follow"><meta http-equiv="refresh" content="0; url={target}"></head>'
                 f'<body><a href="{target}">{SITE}{target}</a></body></html>\n', encoding="utf-8")


def build_404():
    body = '<section class="mx-auto max-w-2xl px-4 py-20 text-center"><h1 class="font-head text-4xl font-extrabold">404</h1>' + "".join(
        f'<p class="mt-4 text-zinc-300" lang="{l}"><a href="{home_url(l)}" class="font-semibold text-brand-300">{HOME[l]["h1"]}</a></p>' for l in LANGS) + "</section>"
    html = page("ka", "/404.html", {l: home_url(l) for l in LANGS}, "404 — Eqskavatori.ge", HOME["ka"]["desc"], "", [], body, "404")
    html = html.replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    html = re.sub(r'<link rel="canonical"[^>]*>\n|<link rel="alternate"[^>]*>\n', "", html)
    (ROOT / "404.html").write_text(html, encoding="utf-8")


# ------------------------------------------------------------------ AI files, sitemap, robots
def markdown(lang, d):
    U = UI[lang]
    out = [f"# {d['h1']}", "", d["lead"], ""]
    for h, items in d["sections"]:
        out += [f"## {h}", ""] + [f"- {x}" for x in items] + [""]
    out += [f"## {U['faq']}", ""]
    for q, a in d["faq"]:
        out += [f"### {q}", "", a, ""]
    out += [f"## {U['contact_h']}", "", f"- {U['phone']}: [{PHONE_FMT}](tel:{PHONE}) · WhatsApp: https://wa.me/{WA}",
            f"- {U['email']}: {EMAIL}", f"- {U['area']}: {U['area_v']}", "", f"Source: {SITE}{d['url']}", ""]
    return "\n".join(out)


def write_md(lang, d):
    md = f"---\ntitle: {d['title']}\nurl: {SITE}{d['url']}\nlang: {lang}\n---\n\n" + markdown(lang, d)
    base = out_file(d["url"])
    base.with_name("index.md").write_text(md, encoding="utf-8")
    base.with_name("index.html.md").write_text(md, encoding="utf-8")
    return md


def sitemap(groups):
    xs = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    for urls, prio in groups:
        for l in LANGS:
            xs.append(f"  <url>\n    <loc>{SITE}{urls[l]}</loc>\n    <lastmod>{TODAY}</lastmod>\n    <priority>{prio if l == 'ka' else '0.8'}</priority>")
            xs += [f'    <xhtml:link rel="alternate" hreflang="{a}" href="{SITE}{urls[a]}"/>' for a in LANGS]
            xs.append(f'    <xhtml:link rel="alternate" hreflang="x-default" href="{SITE}{urls["ka"]}"/>\n  </url>')
    xs.append("</urlset>\n")
    p = ROOT / "sitemap.xml"
    new = "\n".join(xs)
    if p.exists():   # keep lastmod stable when nothing else changed (idempotent builds)
        old = p.read_text(encoding="utf-8")
        if re.sub(r"<lastmod>[^<]*</lastmod>", "", old) == re.sub(r"<lastmod>[^<]*</lastmod>", "", new):
            return
    p.write_text(new, encoding="utf-8")


def robots():
    bots = ["Googlebot", "Bingbot", "GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended", "Applebot", "YandexBot"]
    txt = "User-agent: *\nAllow: /\n\n" + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in bots) + f"Sitemap: {SITE}/sitemap.xml\n"
    (ROOT / "robots.txt").write_text(txt, encoding="utf-8")


def llms(all_md):
    lines = [f"# {BRAND}", "",
             "> Mini excavator services with an operator in Tbilisi, Georgia (and surroundings): earthworks, trench digging, foundation excavation, "
             "septic tank installation, sewer and water line installation, site levelling, hydraulic breaker (concrete breaking), post hole drilling (auger), "
             "demolition, landscaping and construction debris removal with our own truck. The machine always comes with our operator. "
             "Prices are agreed in advance by phone/WhatsApp (they depend on the job). Languages: Georgian, English, Russian.", "",
             f"- Phone / WhatsApp: {PHONE} ({PHONE_FMT}) — https://wa.me/{WA}", f"- Email: {EMAIL}", "- Area: Tbilisi and surroundings; further by agreement", "",
             "## Pages (Georgian · English · Russian)", "",
             f"- Home: {SITE}/ · {SITE}/en/ · {SITE}/ru/"]
    for s in S:
        lines.append(f"- {s['en']['h1']} ({s['ka']['h1']}): {SITE}{svc_url(s, 'ka')} · {SITE}{svc_url(s, 'en')} · {SITE}{svc_url(s, 'ru')}")
    lines.append(f"- Guide — what can a mini excavator do: {SITE}/ka/{GUIDE['slug']['ka']}/ · {SITE}/en/{GUIDE['slug']['en']}/ · {SITE}/ru/{GUIDE['slug']['ru']}/")
    lines += ["", "## Machine-readable copies", "", "Every page has a Markdown copy at <page>/index.md (also index.html.md). Full text of all pages: "
              f"{SITE}/llms-full.txt", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "llms-full.txt").write_text(f"# {BRAND} — full text of all pages\n\n" + "\n\n---\n\n".join(all_md), encoding="utf-8")


def stamp_css():
    """Cache-busting: link every page to styles.css?v=<content hash>. Run after the Tailwind build."""
    import hashlib
    v = hashlib.md5((ROOT / "assets" / "styles.css").read_bytes()).hexdigest()[:8]
    n = 0
    for p in ROOT.glob("**/*.html"):
        if "node_modules" in p.parts:
            continue
        t = p.read_text(encoding="utf-8")
        u = re.sub(r'href="/assets/styles\.css(\?v=[0-9a-f]+)?"', f'href="/assets/styles.css?v={v}"', t)
        if u != t:
            p.write_text(u, encoding="utf-8")
            n += 1
    print(f"styles.css?v={v} stamped on {n} pages")


def main():
    if sys.argv[1:] == ["stamp"]:
        return stamp_css()
    all_md, groups = [], []
    for lang in LANGS:
        all_md.append(write_md(lang, build_home(lang)))
    groups.append(({l: home_url(l) for l in LANGS}, "1.0"))
    for s in S:
        for lang in LANGS:
            all_md.append(write_md(lang, build_service(s, lang)))
        groups.append(({l: svc_url(s, l) for l in LANGS}, "0.9"))
    for lang in LANGS:
        all_md.append(write_md(lang, build_guide(lang)))
    groups.append(({l: f"/{l}/{GUIDE['slug'][l]}/" for l in LANGS}, "0.7"))
    stub("ka/index.html", "/")
    build_404()
    sitemap(groups)
    robots()
    llms(all_md)
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    print(f"built {len(groups) * 3} pages (+ /ka/ redirect, 404), md copies, sitemap, robots, llms")


if __name__ == "__main__":
    main()
