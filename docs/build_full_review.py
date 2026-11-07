"""Build docs/full-review.html: the full write-up as one HTML page, with the figures as live HTML
(taken from readme-visuals.html) instead of PNG screenshots.

    python3 docs/build_full_review.py

Needs: pip install markdown
"""
import re
from pathlib import Path
import markdown

DOCS = Path(__file__).parent
md_src = (DOCS / "FULL_WRITEUP.md").read_text()
vis = (DOCS / "readme-visuals.html").read_text()

# ---- pieces from the figure file
fig_css = re.search(r"<style>(.*?)</style>", vis, re.S).group(1)
fig_css = fig_css.replace("body { margin: 0; background: var(--paper); color: var(--ink); font: 400 16px/1.5 \"Plex Sans\", sans-serif; }", "")
figures = {m.group(1): m.group(0) for m in re.finditer(r'<figure id="(\w+)">.*?</figure>', vis, re.S)}
chart_js = re.search(r"<script>(.*?)</script>", vis, re.S).group(1)

# ---- markdown: GitHub alerts become callouts
LABEL = {"NOTE": "Note", "TIP": "Tip", "IMPORTANT": "Important", "WARNING": "Warning", "CAUTION": "Caution"}


def alerts(text):
    out, lines, i = [], text.split("\n"), 0
    while i < len(lines):
        m = re.match(r"> \[!(\w+)\]\s*$", lines[i])
        if m:
            kind = m.group(1)
            body = []
            i += 1
            while i < len(lines) and lines[i].startswith(">"):
                body.append(lines[i][1:].lstrip(" ") if lines[i] != ">" else "")
                i += 1
            inner = markdown.markdown("\n".join(body), extensions=["tables"])
            out.append(f'<div class="callout co-{kind.lower()}"><div class="callout-label">{LABEL.get(kind, kind)}</div>{inner}</div>')
            continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


src = alerts(md_src)
src = re.sub(r"(?m)^ {2,3}(- |\d+\. )", r"    \1", src)
# drop the hand-written "On this page" list; the page builds its own contents rail
src = re.sub(r"### On this page\n\n(?:\d+\..*\n)+", "", src)
# image placeholders -> figure markers (filled after markdown so markdown doesn't touch the HTML)
src = re.sub(r'<img src="img/(\w+)\.png"[^>]*>', lambda m: f"\n\nFIGURE::{m.group(1)}\n\n", src)

md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "md_in_html"],
                       extension_configs={"toc": {"slugify": lambda v, s: re.sub(r"[^a-z0-9]+", "-", v.lower()).strip("-")}})
body = md.convert(src)
body = re.sub(r"<thead>\s*<tr>\s*(?:<th></th>\s*)+</tr>\s*</thead>", "", body)
body = re.sub(r"(?s)(<table>.*?</table>)", r'<div class="table-scroll">\1</div>', body)
body = re.sub(r"<p>FIGURE::(\w+)</p>", lambda m: f'<div class="fig-wrap">{figures[m.group(1)]}</div>', body)
# links inside the repo: keep them working from docs/
toc = [(m.group(1), re.sub("<.*?>", "", m.group(2))) for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', body)]
toc_html = "\n".join(f'<li><a href="#{i}">{t}</a></li>' for i, t in toc)

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Prompt-writing skill: full review</title>
<meta name="description" content="How a prompt from MIT CSAIL's weight-editing work became a Claude skill, and what two evaluation rounds showed.">
<style>
{fig_css}
  /* ---------- page ---------- */
  html {{ scroll-behavior: smooth; }}
  @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} }}
  body {{ margin: 0; background: var(--paper); color: var(--ink); font: 400 16px/1.6 "Plex Sans", system-ui, sans-serif; }}
  .layout {{ display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 40px; max-width: 1480px; margin: 0 auto; padding: 32px 32px 80px; }}
  nav.rail {{ position: sticky; top: 24px; align-self: start; font-size: 14px; }}
  nav.rail .title {{ font: 600 15px "Source Serif", serif; margin: 0 0 12px; }}
  nav.rail ol {{ list-style: none; padding: 0; margin: 0; counter-reset: s; }}
  nav.rail li {{ margin: 0; }}
  nav.rail a {{ display: block; padding: 6px 10px; border-left: 2px solid var(--rule); color: var(--ink-soft); text-decoration: none; line-height: 1.35; }}
  nav.rail a:hover {{ color: var(--ink); border-color: var(--ink-soft); }}
  nav.rail a.on {{ color: var(--cobalt); border-color: var(--cobalt); font-weight: 500; }}
  nav.rail a:focus-visible, main a:focus-visible {{ outline: 2px solid var(--cobalt); outline-offset: 2px; }}
  main {{ min-width: 0; }}
  .sheet {{ background: var(--sheet); border: 1px solid var(--rule); border-radius: 6px; padding: 40px 56px 56px; }}
  .sheet > :first-child {{ margin-top: 0; }}
  .sheet > h2 {{ font: 600 30px/1.2 "Source Serif", serif; margin: 56px 0 16px; padding-top: 8px; scroll-margin-top: 16px; }}
  .sheet > h3 {{ font: 600 21px/1.3 "Source Serif", serif; margin: 36px 0 10px; scroll-margin-top: 16px; }}
  .sheet > p, .sheet > ul > li, .sheet > ol > li {{ max-width: 76ch; }}
  .sheet li li {{ max-width: 72ch; }}
  main a {{ color: var(--cobalt); text-underline-offset: 2px; }}
  .sheet code {{ font: 400 0.88em "Plex Mono", monospace; background: var(--paper); border: 1px solid var(--rule); border-radius: 3px; padding: 1px 5px; }}
  .sheet > pre {{ background: var(--paper); border: 1px solid var(--rule); border-radius: 4px; padding: 16px 18px; overflow-x: auto; }}
  .sheet > pre code {{ border: 0; padding: 0; background: none; font-size: 13.5px; line-height: 1.6; }}
  .table-scroll table {{ border-collapse: collapse; margin: 18px 0 24px; font-size: 14.5px; width: 100%; }}
  .table-scroll th, .table-scroll td {{ border: 1px solid var(--rule); padding: 8px 12px; text-align: left; vertical-align: top; }}
  .table-scroll th {{ background: var(--paper); font-weight: 600; }}
  .sheet > hr {{ border: 0; border-top: 1px solid var(--rule); margin: 40px 0; }}
  .table-scroll {{ overflow-x: auto; }}
  .callout {{ border: 1px solid var(--rule); border-left: 4px solid var(--c); background: var(--bg); border-radius: 4px; padding: 14px 18px; margin: 20px 0; }}
  .callout p, .callout li {{ max-width: none; }}
  .callout > :last-child {{ margin-bottom: 0; }}
  .callout-label {{ font-weight: 600; color: var(--c); font-size: 14px; margin-bottom: 4px; }}
  .callout.co-note {{ --c: #2448B8; --bg: #F3F6FF; }}
  .callout.co-tip {{ --c: #1C6B3C; --bg: #F1FAF4; }}
  .callout.co-important {{ --c: #6A3FC4; --bg: #F6F2FF; }}
  .callout.co-warning {{ --c: #9A6200; --bg: #FFF8E6; }}
  .callout.co-caution {{ --c: #B4361E; --bg: #FFF3F0; }}
  .fig-wrap {{ overflow-x: auto; margin: 28px -16px; padding: 0 16px; }}
  .fig-wrap figure {{ margin: 0 auto; width: auto; min-width: 860px; max-width: 1120px; }}
  #banner {{ margin-bottom: 8px; }}
  footer {{ color: var(--ink-soft); font-size: 13.5px; margin-top: 28px; }}
  @media (max-width: 700px) {{
    .fig-wrap #banner {{ min-width: 0; }}
    #banner h1 {{ font-size: 32px; padding: 12px 20px 0; }}
    #banner .crumbs, #banner .lede {{ padding-left: 20px; padding-right: 20px; }}
    #banner .lede {{ font-size: 17px; }}
    #banner table {{ margin: 20px; display: block; }}
    #banner td {{ display: block; padding: 2px 0; }}
  }}
  @media (max-width: 1100px) {{
    .layout {{ grid-template-columns: 1fr; padding: 16px; gap: 16px; }}
    nav.rail {{ position: static; }}
    .sheet {{ padding: 24px 18px 36px; }}
  }}
</style>
</head>
<body>
<div class="layout">
  <nav class="rail" aria-label="Contents">
    <p class="title">On this page</p>
    <ol>{toc_html}</ol>
  </nav>
  <main>
    <div class="sheet">
{body}
    </div>
    <footer>Generated from <code>docs/FULL_WRITEUP.md</code> and <code>docs/readme-visuals.html</code> by <code>docs/build_full_review.py</code>.</footer>
  </main>
</div>
<script>
{chart_js}
  // highlight the current section in the contents rail
  const links = [...document.querySelectorAll("nav.rail a")];
  const map = new Map(links.map(a => [a.getAttribute("href").slice(1), a]));
  const obs = new IntersectionObserver(es => {{
    es.forEach(e => {{ if (e.isIntersecting) {{ links.forEach(a => a.classList.remove("on")); map.get(e.target.id)?.classList.add("on"); }} }});
  }}, {{ rootMargin: "0px 0px -70% 0px" }});
  document.querySelectorAll("main h2[id]").forEach(h => obs.observe(h));
</script>
</body>
</html>
"""
(DOCS / "full-review.html").write_text(page)
print("wrote", DOCS / "full-review.html", f"{len(page)//1024} KB, {len(toc)} sections, {len(figures)} figures available")
