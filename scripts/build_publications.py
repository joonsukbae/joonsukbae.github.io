#!/usr/bin/env python3
"""Convert publications.bib + curated metadata into publications/index.html.

Tiny, dependency-free BibTeX reader. Designed for the small set of entries
we maintain by hand.
"""

from __future__ import annotations

import html
import re
from pathlib import Path
from typing import Any

BIB = Path("/Users/js/Library/Mobile Documents/com~apple~CloudDocs/Lab./CV/source/publications.bib")
OUT = Path("/Users/js/personal/joonsukbae.github.io/publications/index.html")
ME_LAST = "Bae"
ME_FIRST = "Joonsuk"


# ---------- BibTeX parser (small, forgiving) ----------

def _strip_braces(s: str) -> str:
    s = s.strip()
    while len(s) >= 2 and ((s[0] == "{" and s[-1] == "}") or (s[0] == '"' and s[-1] == '"')):
        s = s[1:-1].strip()
    return s


def parse_bib(text: str) -> list[dict[str, Any]]:
    entries = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "@":
            i += 1
            continue
        # entry type
        m = re.match(r"@(\w+)\s*\{\s*([^,]+),", text[i:])
        if not m:
            i += 1
            continue
        etype = m.group(1).lower()
        key = m.group(2).strip()
        i += m.end()
        # find matching closing brace by counting
        depth = 1
        start = i
        while i < n and depth > 0:
            c = text[i]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            i += 1
        body = text[start:i - 1]

        fields: dict[str, str] = {"_type": etype, "_key": key}
        # parse field = value, splitting on top-level commas
        j = 0
        L = len(body)
        while j < L:
            # skip whitespace and commas
            while j < L and body[j] in " \t\r\n,":
                j += 1
            if j >= L:
                break
            # read field name
            fm = re.match(r"([A-Za-z][A-Za-z0-9_-]*)\s*=\s*", body[j:])
            if not fm:
                break
            field = fm.group(1).lower()
            j += fm.end()
            # read value: either {...} (balanced) or "..." or until comma
            if j < L and body[j] == "{":
                d = 1
                vs = j + 1
                j += 1
                while j < L and d > 0:
                    if body[j] == "{":
                        d += 1
                    elif body[j] == "}":
                        d -= 1
                    j += 1
                val = body[vs:j - 1]
            elif j < L and body[j] == '"':
                vs = j + 1
                j += 1
                while j < L and body[j] != '"':
                    j += 1
                val = body[vs:j]
                j += 1  # skip closing "
            else:
                vs = j
                while j < L and body[j] != ",":
                    j += 1
                val = body[vs:j]
            fields[field] = val.strip()

        fields["_type"] = etype
        fields["_key"] = key
        entries.append(fields)
    return entries


# ---------- formatters ----------

def format_authors(raw: str) -> str:
    """BibTeX `author` field -> HTML string, highlighting me. Caps `et al.` after 6."""
    # Authors are separated by " and " in BibTeX
    parts = [p.strip() for p in re.split(r"\s+and\s+", raw)]
    pretty = []
    has_et_al = False
    for p in parts:
        p = _strip_braces(p)
        if p.lower() == "others":
            has_et_al = True
            continue
        if "," in p:
            last, first = [x.strip() for x in p.split(",", 1)]
            disp = f"{first} {last}"
        else:
            disp = p
        pretty.append(disp)

    rendered = []
    me_idx = None
    for idx, name in enumerate(pretty):
        is_me = (ME_LAST.lower() in name.lower()) and (ME_FIRST.lower() in name.lower())
        if is_me:
            me_idx = idx
            rendered.append(f'<span class="me">{html.escape(name)}</span>')
        else:
            rendered.append(html.escape(name))

    # Truncate long author lists, but keep me visible
    if len(rendered) > 6:
        if me_idx is not None and me_idx >= 5:
            head = rendered[:4]
            mid = rendered[me_idx]
            return ", ".join(head) + ", &hellip;, " + mid + ", <i>et&nbsp;al.</i>"
        else:
            head = rendered[:5]
            return ", ".join(head) + ", <i>et&nbsp;al.</i>"

    out = ", ".join(rendered)
    if has_et_al:
        out += ", <i>et&nbsp;al.</i>"
    return out


# Tiny LaTeX -> Unicode for the common math we see in titles
_SUP = str.maketrans({
    "0":"⁰","1":"¹","2":"²","3":"³","4":"⁴",
    "5":"⁵","6":"⁶","7":"⁷","8":"⁸","9":"⁹",
    "+":"⁺","-":"⁻"
})
def _detex(s: str) -> str:
    # $^{12}$C  ->  ¹²C ; $e^{+}e^{-}$ -> e⁺e⁻ ; remove stray braces
    def sub_math(m):
        inner = m.group(1)
        # ^{...}
        inner = re.sub(r"\^\{([^}]*)\}", lambda mm: mm.group(1).translate(_SUP), inner)
        inner = re.sub(r"\^([^{\s])", lambda mm: mm.group(1).translate(_SUP), inner)
        # remove remaining $ and braces
        inner = inner.replace("{", "").replace("}", "")
        return inner
    s = re.sub(r"\$([^$]+)\$", sub_math, s)
    # en-dash normalization
    s = s.replace("--", "–")
    return s


def format_venue(e: dict[str, Any]) -> str:
    j = e.get("journal", "")
    v = e.get("volume", "")
    num = e.get("number", "")
    pages = e.get("pages", "")
    year = e.get("year", "")
    parts = []
    if j:
        parts.append(f"<em>{html.escape(j)}</em>")
    vstr = ""
    if v:
        vstr += f" <b>{html.escape(v)}</b>"
    if pages:
        vstr += f", {html.escape(pages)}"
    if year:
        vstr += f" ({html.escape(year)})"
    if vstr:
        parts.append(vstr.lstrip())
    return " ".join(parts)


def doi_url(e: dict[str, Any]) -> str | None:
    d = e.get("doi", "").strip()
    if not d:
        return None
    if d.startswith("http"):
        return d
    return f"https://doi.org/{d}"


def arxiv_url(e: dict[str, Any]) -> str | None:
    a = e.get("eprint", "").strip()
    if not a:
        return None
    return f"https://arxiv.org/abs/{a}"


def explicit_url(e: dict[str, Any]) -> str | None:
    u = e.get("url", "").strip()
    return u if u else None


# ---------- curated metadata (role, tag) ----------

# Manually-curated additions per CV ordering
CURATED: dict[str, dict[str, str]] = {
    "Cho:2025drcalo": {
        "role": "Contribution to dual-readout calorimeter module construction.",
        "tag":  "Co-author",
    },
    "Kim:2025lamps": {
        "role": "Support for Time-of-Flight detector maintenance and on-site checks.",
        "tag":  "Collaboration",
    },
    "Kim:2024jinst": {
        "role": "Contribution to forward tracking detector R&amp;D and performance studies.",
        "tag":  "Co-author",
    },
    "LAMPS:2021mhm": {
        "role": "Contribution to SiPM and scintillator-based detector R&amp;D.",
        "tag":  "Collaboration",
    },
}


# ---------- HTML page ----------

PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Publications — Joonsuk Bae</title>
  <meta name="description" content="Publications by Joonsuk Bae. Full INSPIRE-HEP list linked.">
  <link rel="stylesheet" href="/assets/css/style.css">
  <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' fill='%23fafaf7'/%3E%3Crect x='12' y='12' width='8' height='8' fill='%239b2c2c'/%3E%3C/svg%3E">
</head>
<body>
<div class="page">

  <header class="site-header">
    <div class="brand">
      <a href="/"><span class="mark" aria-hidden="true"></span>Joonsuk&nbsp;Bae</a>
    </div>
    <nav class="nav" aria-label="Primary">
      <a href="/">Home</a>
      <a href="/research/">Research</a>
      <a href="/publications/" class="is-current">Publications</a>
      <a href="/talks/">Talks</a>
      <a href="/cv/">CV</a>
      <a href="/contact/">Contact</a>
    </nav>
  </header>

  <main>

    <h1>Publications</h1>
    <p class="lede">A maintained list of non-collaboration publications. Full publication record, including the ALICE collaboration papers I co-author since October&nbsp;2022, is on <a href="https://inspirehep.net/authors/2117232">INSPIRE&ndash;HEP</a>.</p>

    <section>
      <div class="grid">
        <div class="label">Non-collab</div>
        <div class="col">
          <h2>Selected non-collaboration publications</h2>
          <div class="list">
{PUBS}
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="grid">
        <div class="label">In&nbsp;prep</div>
        <div class="col">
          <h2>In preparation</h2>
          <div class="list">
            <div class="pub">
              <div class="num">&mdash;</div>
              <div class="body">
                <div class="ptitle"><em>Charged-particle jet cross sections in pp collisions at &radic;<i>s</i>&thinsp;=&thinsp;13.6&nbsp;TeV with ALICE.</em></div>
                <div class="venue">ALICE Collaboration, in preparation.</div>
                <div class="role"><span class="tag">Lead</span>Lead analyzer.</div>
              </div>
            </div>
            <div class="pub">
              <div class="num">&mdash;</div>
              <div class="body">
                <div class="ptitle"><em>Beam-test studies of Pb/SciFi calorimeter prototypes for the Electron&ndash;Ion Collider.</em></div>
                <div class="venue">ePIC BIC, three papers in preparation.</div>
                <div class="role"><span class="tag">Co-author</span>Data analysis and module production.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <section>
      <div class="grid">
        <div class="label">Collab</div>
        <div class="col">
          <h2>ALICE collaboration papers</h2>
          <p class="prose">Co-author on ALICE Collaboration papers since October&nbsp;2022 (109 collaboration papers and counting). The complete list, with citation metrics, is maintained on INSPIRE&ndash;HEP.</p>
          <p class="quick" style="margin-top: var(--s-5);">
            <a href="https://inspirehep.net/authors/2117232">Full list on INSPIRE&ndash;HEP &rarr;</a>
            <a href="https://orcid.org/0009-0008-4806-8019">ORCID profile &rarr;</a>
          </p>
        </div>
      </div>
    </section>

  </main>

  <footer class="site-footer">
    <div>&copy; 2026 Joonsuk Bae</div>
    <div>Last updated 2026.05</div>
  </footer>

</div>
</body>
</html>
"""


def render_entry(idx: int, e: dict[str, Any]) -> str:
    title = _detex(_strip_braces(e.get("title", "")).strip().rstrip("."))
    authors = format_authors(e.get("author", ""))
    venue = _detex(format_venue(e))
    links = []
    if (u := doi_url(e)):
        links.append(f'<a href="{html.escape(u)}">DOI</a>')
    if (u := arxiv_url(e)):
        links.append(f'<a href="{html.escape(u)}">arXiv</a>')
    if (u := explicit_url(e)) and not e.get("doi"):
        links.append(f'<a href="{html.escape(u)}">Link</a>')
    links_html = ""
    if links:
        links_html = '<div class="links">' + "".join(links) + "</div>"

    curated = CURATED.get(e["_key"], {})
    role_html = ""
    if curated:
        tag = curated.get("tag", "")
        role = curated.get("role", "")
        tag_html = f'<span class="tag">{tag}</span>' if tag else ""
        role_html = f'<div class="role">{tag_html}{role}</div>'

    return f"""            <div class="pub">
              <div class="num">{idx:02d}</div>
              <div class="body">
                <div class="authors">{authors}</div>
                <div class="ptitle">{html.escape(title)}.</div>
                <div class="venue">{venue}</div>
                {role_html}
                {links_html}
              </div>
            </div>"""


def main() -> None:
    text = BIB.read_text(encoding="utf-8")
    entries = parse_bib(text)
    # newest first by year
    def year_of(e):
        try:
            return int(e.get("year", "0"))
        except ValueError:
            return 0
    entries.sort(key=year_of, reverse=True)

    rendered = "\n".join(render_entry(i + 1, e) for i, e in enumerate(entries))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(PAGE.replace("{PUBS}", rendered), encoding="utf-8")
    print(f"Wrote {OUT} with {len(entries)} entries.")


if __name__ == "__main__":
    main()
