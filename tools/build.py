"""Build the Agent SOC site.

    python tools/build.py

Reads src/game.html (one page, both languages inside) and writes ru/index.html and
en/index.html with per-language metadata, a root index.html that sends visitors to their
language, and sitemap.xml.
"""
import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://nibrmi.github.io/agent-soc/"

META = {
    "ru": {
        "TITLE": "Agent SOC — игра про безопасность AI-агентов",
        "DESC": "Побудь службой безопасности для 10 000 AI-агентов: вручную, с ИИ-надзирателем и с архитектурой, "
                "которую нельзя уговорить. 3 минуты, по мотивам реальных инцидентов.",
        "LOCALE": "ru_RU",
        "NOSCRIPT": "Для игры нужен JavaScript.",
    },
    "en": {
        "TITLE": "Agent SOC — a game about AI agent security",
        "DESC": "Run security for 10,000 AI agents: by hand, with an AI supervisor, and with architecture "
                "that can’t be talked round. 3 minutes, based on real incidents.",
        "LOCALE": "en_US",
        "NOSCRIPT": "This game needs JavaScript.",
    },
}

ROOT_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Agent SOC</title>
<link rel="canonical" href="{site}en/">
<link rel="alternate" hreflang="ru" href="{site}ru/">
<link rel="alternate" hreflang="en" href="{site}en/">
<link rel="alternate" hreflang="x-default" href="{site}en/">
<meta property="og:title" content="Agent SOC — a game about AI agent security">
<meta property="og:image" content="{site}og-en.png">
<script>
  var l = (navigator.languages || [navigator.language || ""]).join(",").toLowerCase();
  location.replace(/(^|,)ru/.test(l) ? "ru/" : "en/");
</script>
<style>body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#0A0F1C;color:#E8EEF8;font:16px system-ui,sans-serif}}a{{color:#5B8DFF;margin:0 10px}}</style>
</head>
<body><p>Agent SOC: <a href="en/" hreflang="en">English</a><a href="ru/" hreflang="ru" lang="ru">Русский</a></p></body>
</html>
"""

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
{urls}
</urlset>
"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def main():
    with io.open(os.path.join(ROOT, "src", "game.html"), encoding="utf-8") as f:
        src = f.read()
    for lang, meta in META.items():
        values = dict(meta, LANG=lang, URL=SITE + lang + "/", OG=SITE + "og-" + lang + ".png")
        page = re.sub(r"\{\{(\w+)\}\}", lambda m: values[m.group(1)], src)
        if "{{" in page:
            sys.exit("unfilled placeholder in %s page" % lang)
        write(os.path.join(ROOT, lang, "index.html"), page)
    write(os.path.join(ROOT, "index.html"), ROOT_PAGE.format(site=SITE))
    alts = "".join('\n    <xhtml:link rel="alternate" hreflang="%s" href="%s%s/"/>' % (l, SITE, l) for l in ("ru", "en"))
    urls = "\n".join("  <url>\n    <loc>%s%s/</loc>%s\n  </url>" % (SITE, l, alts) for l in ("en", "ru"))
    write(os.path.join(ROOT, "sitemap.xml"), SITEMAP.format(urls=urls))
    print("built ru/, en/, index.html and sitemap.xml")


if __name__ == "__main__":
    main()
