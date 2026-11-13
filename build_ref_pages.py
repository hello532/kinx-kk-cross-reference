#!/usr/bin/env python3
"""Generate the human-readable reference pages for the GitHub Pages mirror.

Every row links to the matching page on kinxfa.com, so the mirror becomes a
dofollow hub pointing at the product pages instead of a dead-end dataset.
"""
import csv, html, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "data", "kinx-kk-cross-reference.csv")
SITE = "https://hello532.github.io/kinx-kk-cross-reference"
MAIN = "https://kinxfa.com"

def target(size, lead):
    key = (size, lead.split(" ")[0])
    return {
        ("KK50", "2"): "/pages/kk50",
        ("KK60", "5"): "/pages/kk6005",
        ("KK60", "10"): "/pages/kk60",
        ("KK60", "20"): "/pages/kk6020",
        ("KK86", "10"): "/pages/kk8610",
        ("KK86", "20"): "/pages/kk8620",
    }.get(key, "/pages/kk-modules")

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<style>
:root{{--fg:#111;--mut:#5b6470;--line:#e3e6ea;--acc:#0b5fff;--bg:#fff}}
*{{box-sizing:border-box}}
body{{margin:0;padding:32px 20px 72px;font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:var(--fg);background:var(--bg);max-width:980px;margin-inline:auto}}
h1{{font-size:1.9rem;line-height:1.25;margin:0 0 .4em}}
h2{{font-size:1.3rem;margin:2em 0 .5em;padding-top:.2em}}
h3{{font-size:1.05rem;margin:1.4em 0 .3em}}
p,li{{color:#222}}
.lede{{color:var(--mut);font-size:1.05rem}}
a{{color:var(--acc);text-decoration:none}}
a:hover{{text-decoration:underline}}
table{{width:100%;border-collapse:collapse;font-size:.92rem;margin:1em 0}}
th,td{{text-align:left;padding:7px 9px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{background:#f6f8fa;font-weight:600;position:sticky;top:0}}
td.n{{font-variant-numeric:tabular-nums}}
code{{font:13px/1.4 ui-monospace,SFMono-Regular,Menlo,monospace;background:#f4f6f8;padding:1px 5px;border-radius:4px}}
.note{{border-left:3px solid var(--acc);padding:.6em 0 .6em 1em;color:var(--mut);margin:1.5em 0;background:#fafbfc}}
footer{{margin-top:3em;padding-top:1.2em;border-top:1px solid var(--line);color:var(--mut);font-size:.88rem}}
</style>
{jsonld}
</head><body>
"""

TAIL = """<footer>
<p>Reference data: <a href="{site}/">KINX KK cross-reference dataset</a> &middot;
DOI <a href="https://doi.org/10.5281/zenodo.24182082">10.5281/zenodo.24182082</a> &middot;
raw <a href="{site}/data/kinx-kk-cross-reference.csv">CSV</a> /
<a href="{site}/data/kinx-kk-cross-reference.json">JSON</a> &middot; CC BY 4.0.</p>
<p>Product pages and prices: <a href="{main}/pages/hiwin-kk-part-number-decoder">kinxfa.com</a>.
This page is an independent reference; always confirm against a drawing before ordering.</p>
</footer></body></html>"""

def write(path, title, desc, canonical, jsonld, body):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ld = '<script type="application/ld+json">' + json.dumps(jsonld, ensure_ascii=False, indent=1) + "</script>"
    doc = HEAD.format(title=title, desc=desc, url=canonical, jsonld=ld) if False else None
    doc = (HEAD.replace("{title}", title).replace("{desc}", desc).replace("{url}", canonical)
               .replace("{jsonld}", ld))
    doc += body + TAIL.replace("{site}", SITE).replace("{main}", MAIN)
    open(path, "w", encoding="utf-8").write(doc)
    print("wrote", path, len(doc), "B")

rows = list(csv.DictReader(open(CSV, encoding="utf-8")))

# ---------- page 1: the decoded table ----------
tr = []
for r in rows:
    href = MAIN + target(r["Size"], r["Lead"])
    build = r["KINX build"].split("·")[0].strip()
    price = r["KINX build"].split("·")[1].strip() if "·" in r["KINX build"] else ""
    tr.append(
        f'<tr><td><code>{html.escape(r["Part number"])}</code></td>'
        f'<td>{html.escape(r["Size"])}</td>'
        f'<td class="n">{html.escape(r["Lead"])}</td>'
        f'<td>{html.escape(r["Grade"])}</td>'
        f'<td class="n">{html.escape(r["Rail"])}</td>'
        f'<td class="n">{html.escape(r["Max stroke (1 block)"])}</td>'
        f'<td><a href="{href}">{html.escape(build)}</a></td>'
        f'<td class="n">{html.escape(price)}</td></tr>'
    )

body = f"""<h1>HIWIN KK part numbers, decoded: 56 models across KK50, KK60 and KK86</h1>
<p class="lede">A static table of every KK part number we cross-reference, with frame size, screw lead,
accuracy grade, rail length and the KINX build that matches the mounting dimensions. Each row links to the
page for that size and lead.</p>
<p>The point of the table is narrow: a KK part number encodes four things that must all match before a
replacement fits &mdash; <strong>frame size</strong>, <strong>screw lead</strong>, <strong>rail length</strong>
and the <strong>block type</strong>. Two numbers that differ in one character can be 30&nbsp;mm apart in
combined height. So decode first, then measure.</p>
<h2>The table</h2>
<table><thead><tr><th>Part number</th><th>Size</th><th>Lead</th><th>Grade</th><th>Rail</th><th>Max stroke (1 block)</th><th>KINX build</th><th>From</th></tr></thead>
<tbody>
{chr(10).join(tr)}
</tbody></table>
<div class="note"><strong>Reading the grade column.</strong> <code>Normal (C)</code> and <code>Precision (P)</code>
are accuracy grades, not quality tiers. A C-grade module is not a defective P-grade one; the difference is
running parallelism and the resulting positional deviation over the stroke. If your machine repeats to
&plusmn;0.02&nbsp;mm, grade matters more than the part number suggests. Ask for the grade on the drawing, not
on the quote.</div>
<h2>How to read a KK part number</h2>
<p>Take <code>KK6010P-500A1-F0</code>. Split it at the dashes and read right to left:</p>
<ul>
<li><code>KK</code> &mdash; the series. KK is the ball-screw-driven linear module family; the number that
follows is the frame width in tens of millimetres (KK50 &rarr; 50&nbsp;mm, KK60 &rarr; 60&nbsp;mm,
KK86 &rarr; 86&nbsp;mm).</li>
<li><code>10</code> &mdash; screw lead in millimetres per revolution. This single number drives speed, thrust
and resolution at once, which is why it is the first thing to fix in a design.</li>
<li><code>P</code> &mdash; accuracy grade, <code>C</code> (normal) or <code>P</code> (precision).</li>
<li><code>500</code> &mdash; rail length in millimetres. Stroke is what is left after the block and the
end caps, so stroke is always shorter than rail.</li>
<li><code>A1</code> &mdash; block and preload configuration.</li>
<li><code>F0</code> &mdash; the motor interface: flange pattern, coupling and whether a cover is fitted.</li>
</ul>
<p>Most substitution failures come from the last field. The frame, lead and rail can match perfectly and the
motor flange still not fit, because <code>F0</code> and <code>F1</code> are different flange patterns for the
same body. Measure the flange bolt circle and the coupling bore before you compare prices.</p>
<h2>What this table does not tell you</h2>
<p>Maximum stroke with one block is listed as <em>confirm on drawing</em> wherever the catalogue does not
state it unambiguously. That is deliberate: the usable stroke depends on the end-cap style and whether a
cover is fitted, and we would rather leave a cell empty than publish a number that costs somebody a scrapped
part. The <a href="{SITE}/">dataset page</a> carries the same caveat in machine-readable form, and the
<a href="{MAIN}/pages/hiwin-kk-part-number-decoder">decoder on kinxfa.com</a> lets you filter by size.</p>
<h2>Next steps</h2>
<ul>
<li>Sizing the screw for thrust and speed? Start with
<a href="{MAIN}/pages/kk60">KK60 linear module</a> and the lead comparison below.</li>
<li>Replacing an existing HIWIN unit? Read
<a href="{MAIN}/pages/hiwin-kk-replacement">the replacement checklist</a> first &mdash; four dimensions have
to match, and only two of them are in the part number.</li>
<li>Need the table offline? <a href="{SITE}/data/kinx-kk-cross-reference.csv">Download the CSV</a>
(56 rows, CC BY 4.0) or the <a href="{SITE}/data/kinx-kk-cross-reference.json">JSON</a>.</li>
</ul>
<h2>Related reference</h2>
<ul><li><a href="{SITE}/ref/kk60-lead-selection/">KK60 lead selection: 5, 10 or 20 mm</a></li>
<li><a href="{SITE}/">Dataset home</a></li></ul>
"""
ld = {
 "@context": "https://schema.org",
 "@type": "TechArticle",
 "headline": "HIWIN KK part numbers, decoded: 56 models across KK50, KK60 and KK86",
 "description": "Static cross-reference of 56 HIWIN KK linear module part numbers with frame size, screw lead, accuracy grade, rail length and the matching KINX build.",
 "url": f"{SITE}/ref/",
 "isPartOf": {"@type": "Dataset", "name": "KINX KK cross-reference",
              "identifier": "10.5281/zenodo.24182082"},
 "license": "https://creativecommons.org/licenses/by/4.0/",
 "publisher": {"@type": "Organization", "name": "KINX Linear Modules", "url": MAIN + "/"},
 "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
   {"@type": "ListItem", "position": 1, "name": "Dataset", "item": SITE + "/"},
   {"@type": "ListItem", "position": 2, "name": "KK part number table", "item": f"{SITE}/ref/"}]},
}
body = body.replace("{SITE}", SITE).replace("{MAIN}", MAIN)
write(os.path.join(HERE, "ref", "index.html"),
      "HIWIN KK part number table: 56 models decoded (KK50 / KK60 / KK86)",
      "Cross-reference table of 56 HIWIN KK part numbers: frame size, screw lead, accuracy grade, rail length, max stroke and the matching KINX build.",
      f"{SITE}/ref/", ld, body)

# ---------- page 2: lead selection ----------
body2 = f"""<h1>KK60 lead selection: what 5, 10 and 20&nbsp;mm actually change</h1>
<p class="lede">Lead is the one number in a KK60 part number that trades speed against thrust against
resolution. Here is the arithmetic, using the same 1&nbsp;mm/rev baseline, so you can pick before you quote.</p>
<h2>The three-way trade</h2>
<p>For a ball screw, thrust and speed move inversely with lead at a fixed motor torque and fixed motor speed:</p>
<table><thead><tr><th>Lead</th><th>Speed at 3000&nbsp;rpm</th><th>Thrust vs 5&nbsp;mm lead</th><th>Resolution per full step (1.8&deg; motor, direct)</th><th>Pick it when</th></tr></thead>
<tbody>
<tr><td class="n">5&nbsp;mm</td><td class="n">15&nbsp;m/min</td><td class="n">1&times; (baseline)</td><td class="n">25&nbsp;&micro;m</td><td>Pressing, clamping, dispensing &mdash; force matters more than cycle time</td></tr>
<tr><td class="n">10&nbsp;mm</td><td class="n">30&nbsp;m/min</td><td class="n">0.5&times;</td><td class="n">50&nbsp;&micro;m</td><td>General pick-and-place; the default compromise</td></tr>
<tr><td class="n">20&nbsp;mm</td><td class="n">60&nbsp;m/min</td><td class="n">0.25&times;</td><td class="n">100&nbsp;&micro;m</td><td>Long transfer moves where the load is light and the stroke is long</td></tr>
</tbody></table>
<p>The numbers above are the direct consequence of lead, not a manufacturer's claim: doubling the lead doubles
the distance per revolution and halves the force per unit of motor torque. The step-resolution column assumes a
1.8&deg; stepper with no microstepping and no gearbox; add a 5:1 planetary and divide by five.</p>
<h2>Where the 20&nbsp;mm lead falls apart</h2>
<p>Two limits show up before the thrust limit does. The first is <strong>critical speed</strong>: a longer screw
whipping at high rpm. The second is <strong>resonance at the stroke ends</strong>, which appears as a
positioning error that only shows up in one direction. On a 1310&nbsp;mm stroke, a 20&nbsp;mm lead is usually
chosen for the transfer moves and then run at half the calculated top speed to stay clear of both. If your
cycle needs the full 60&nbsp;m/min at that stroke, you want a larger frame (KK86), not a longer KK60.</p>
<h2>Where the 5&nbsp;mm lead costs you money</h2>
<p>15&nbsp;m/min at 3000&nbsp;rpm is fine for a press, painful for a gantry. Before you specify 5&nbsp;mm for
thrust, check whether the force you need is actually continuous or only at the moment of contact: a 10&nbsp;mm
lead with a 2:1 belt reduction gives you the same thrust, better resolution and a shorter cycle, at the cost of
one more part in the BOM.</p>
<h2>Mounting dimensions that do not change with lead</h2>
<p>Rail width, combined height, hole pitch and motor flange stay the same across leads within a frame size.
That is why a lead change is usually the cheapest redesign: the machine's mounting plate does not move. It is
also why a "cheaper equivalent" with the same lead can still not fit &mdash; the flange is the field that
breaks.</p>
<h2>Next steps</h2>
<ul>
<li><a href="{MAIN}/pages/kk6005">KK60 with 5&nbsp;mm lead</a> &mdash; thrust-first builds</li>
<li><a href="{MAIN}/pages/kk60">KK60 with 10&nbsp;mm lead</a> &mdash; the general-purpose page</li>
<li><a href="{MAIN}/pages/kk6020">KK60 with 20&nbsp;mm lead</a> &mdash; transfer-first builds</li>
<li><a href="{SITE}/ref/">Full KK part number table</a> (56 models)</li>
</ul>
"""
ld2 = {
 "@context": "https://schema.org",
 "@type": "TechArticle",
 "headline": "KK60 lead selection: what 5, 10 and 20 mm actually change",
 "description": "How screw lead trades speed, thrust and step resolution on a KK60 linear module, with the arithmetic and the two limits that appear before the thrust limit.",
 "url": f"{SITE}/ref/kk60-lead-selection/",
 "isPartOf": {"@type": "Dataset", "name": "KINX KK cross-reference",
              "identifier": "10.5281/zenodo.24182082"},
 "license": "https://creativecommons.org/licenses/by/4.0/",
 "publisher": {"@type": "Organization", "name": "KINX Linear Modules", "url": MAIN + "/"},
 "breadcrumb": {"@type": "BreadcrumbList", "itemListElement": [
   {"@type": "ListItem", "position": 1, "name": "Dataset", "item": SITE + "/"},
   {"@type": "ListItem", "position": 2, "name": "KK part number table", "item": f"{SITE}/ref/"},
   {"@type": "ListItem", "position": 3, "name": "KK60 lead selection",
    "item": f"{SITE}/ref/kk60-lead-selection/"}]},
}
body2 = body2.replace("{SITE}", SITE).replace("{MAIN}", MAIN)
write(os.path.join(HERE, "ref", "kk60-lead-selection", "index.html"),
      "KK60 lead selection: 5, 10 or 20 mm - speed, thrust and resolution",
      "What 5, 10 and 20 mm screw lead change on a KK60 linear module: speed at 3000 rpm, thrust ratio, step resolution and the limits that bite first.",
      f"{SITE}/ref/kk60-lead-selection/", ld2, body2)
