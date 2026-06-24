#!/usr/bin/env python3
"""
generate_roadmap.py — single source of truth -> two HTML roadmaps.

Reads roadmap_data.yaml and produces:
  - ARRO_roadmap.html            (internal: full release timeline + KPIs)
  - ARRO_Roadmap_External.html   (external: quarter cards, no KPIs)

Run after every edit to roadmap_data.yaml:
    python3 generate_roadmap.py
"""
import yaml
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INTERNAL_HTML_PATH = BASE_DIR / "ARRO_Roadmap_Internal.html"
EXTERNAL_HTML_PATH = BASE_DIR / "ARRO_Roadmap_External.html"

with open(BASE_DIR / "roadmap_data.yaml") as f:
    DATA = yaml.safe_load(f)

RELEASES = DATA["releases"]
HORIZON = DATA["horizon"]

TAG_LABELS = {
    "payroll": "Payroll", "operations": "Operations", "platform": "Platform",
    "compliance": "Compliance", "engineering": "Engineering", "technical": "Technical",
    "em": "Emergency Management", "logistics": "Logistics",
}

def fmt_date(iso):
    return datetime.strptime(iso, "%Y-%m-%d").strftime("%m/%d/%y")

def quarters_in_order(items, key):
    return list(dict.fromkeys(it[key] for it in items))

def build_internal_head():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ARRO Internal Roadmap</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;500;600;700&family=Lexend+Deca:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --guardian: #042d49;
      --green: #368604;
      --yellow: #f7b020;
      --horizon: #1075b4;
      --panel: #f5f8fb;
      --border: #c9d8e5;
      --text: #153449;
      --muted: #6a7f90;
      --next-dot: #368604;
      --next-dot-ring: rgba(54, 134, 4, 0.24);
      --upcoming-dot: #f7b020;
      --shipped-dot: #1075b4;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Lexend Deca', sans-serif;
      color: var(--text);
      background: linear-gradient(180deg, #f2f6fa 0%, #e8eff6 100%);
    }
    .page {
      max-width: 1280px;
      margin: 0 auto;
      padding: 20px;
    }
    .topbar {
      background: var(--guardian);
      color: #fff;
      border-radius: 12px;
      padding: 18px 22px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      flex-wrap: wrap;
      box-shadow: 0 8px 24px rgba(4, 45, 73, 0.2);
    }
    .topbar-right { text-align: right; }
    .digest-label {
      font: 700 12px 'Roboto Condensed', sans-serif;
      letter-spacing: 0.1em;
      text-transform: uppercase;
      color: #cbd8e3;
    }
    .last-updated { font-size: 12px; color: #e5edf4; }
    .qtr-nav {
      margin-top: 16px;
      padding: 8px;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 10px;
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }
    .qtr-tab {
      border: 1px solid var(--border);
      background: #fff;
      color: var(--guardian);
      border-radius: 6px;
      padding: 8px 12px;
      font: 600 12px 'Roboto Condensed', sans-serif;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      cursor: pointer;
    }
    .qtr-tab.active {
      background: var(--guardian);
      border-color: var(--guardian);
      color: #fff;
    }
    .qtr-panel {
      display: none;
      margin-top: 14px;
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
    }
    .qtr-panel.active { display: block; }
    .panel-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #d9e4ed;
    }
    .panel-title {
      font: 700 24px 'Roboto Condensed', sans-serif;
      color: var(--guardian);
    }
    .panel-subtitle { font-size: 13px; color: var(--muted); margin-top: 4px; }
    .legend { display: flex; gap: 10px; flex-wrap: wrap; }
    .legend-item { font-size: 12px; color: #445b6d; display: flex; align-items: center; gap: 6px; }
    .legend-dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
    .rows { display: grid; gap: 12px; }
    .release-row {
      display: grid;
      grid-template-columns: 170px 24px minmax(0, 1fr);
      gap: 14px;
      align-items: start;
    }
    .date-col {
      background: var(--panel);
      border: 1px solid #dbe6ef;
      border-radius: 10px;
      padding: 10px;
    }
    .date-val { font: 700 18px 'Roboto Condensed', sans-serif; }
    .rel-num { font-size: 12px; margin-top: 2px; font-weight: 600; }
    .status-label {
      display: inline-block;
      margin-top: 8px;
      padding: 3px 8px;
      border-radius: 999px;
      font-size: 11px;
      font-weight: 600;
    }
    .date-val.next, .rel-num.next { color: #2e6f03; }
    .date-val.upcoming, .rel-num.upcoming { color: #7a5500; }
    .date-val.shipped, .rel-num.shipped { color: #0c447c; }
    .status-label.next { background: #edf6e5; color: #2e6f03; }
    .status-label.upcoming { background: #fef3d9; color: #7a5500; }
    .status-label.shipped { background: #e6f1fb; color: #0c447c; }
    .tl-col { display: flex; flex-direction: column; align-items: center; height: 100%; }
    .tl-dot { width: 12px; height: 12px; border-radius: 50%; margin-top: 8px; }
    .tl-dot.next { background: var(--next-dot); }
    .tl-dot.upcoming { background: var(--upcoming-dot); }
    .tl-dot.shipped { background: var(--shipped-dot); opacity: 0.8; }
    .tl-line { width: 2px; flex: 1; margin-top: 4px; background: #c9d8e5; }
    .tl-line.hidden { visibility: hidden; }
    .feat-col { display: grid; gap: 10px; }
    .feature {
      border: 1px solid var(--border);
      border-left: 4px solid var(--guardian);
      border-radius: 8px;
      padding: 10px 12px;
      background: #fff;
      display: grid;
      gap: 6px;
    }
    .feat-title { font-weight: 600; }
    .multi-note { color: #5f7688; font-size: 12px; font-weight: 400; }
    .feat-value { color: #3f5667; font-size: 14px; }
    .feat-meta { display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.03em;
      border-radius: 999px;
      padding: 2px 8px;
      border: 1px solid #d2e0eb;
      background: #f0f5f9;
      color: #1f465f;
      text-transform: uppercase;
    }
    .tag-multi { background: #fff4db; border-color: #f7d58b; color: #7a5500; }
    .kpi-col { margin-top: 4px; }
    .kpi-container { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }
    .kpi-column {
      border: 1px dashed #bfd0dd;
      background: #f7fbff;
      border-radius: 6px;
      padding: 6px;
      text-align: center;
    }
    .kpi-period { font-size: 11px; color: #4c6374; }
    .kpi-tbd { font-size: 12px; font-weight: 600; color: #28475d; }
    .empty-state {
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      background: #f8fbff;
      margin-bottom: 8px;
    }
    .empty-title { font-weight: 600; }
    .empty-sub { font-size: 14px; color: #456073; margin-top: 4px; }
    @media (max-width: 900px) {
      .release-row { grid-template-columns: 1fr; }
      .tl-col { display: none; }
      .topbar-right { text-align: left; }
    }
  </style>
</head>
'''

def build_external_head():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>ARRO Product Roadmap</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@400;500;600;700&family=Lexend+Deca:wght@300;400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --guardian: #042d49;
      --green: #368604;
      --yellow: #f7b020;
      --horizon: #1075b4;
      --border: #c9d8e5;
      --bg: #edf2f7;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: 'Lexend Deca', sans-serif;
      color: #17374c;
      background: var(--bg);
    }
    .page {
      max-width: 1040px;
      margin: 0 auto;
      padding: 28px 18px 40px;
    }
    header {
      background: var(--guardian);
      color: #fff;
      border-radius: 12px;
      padding: 26px 22px;
      margin-bottom: 16px;
      border-bottom: 4px solid var(--green);
      box-shadow: 0 8px 24px rgba(4, 45, 73, 0.2);
    }
    h1 {
      margin: 0;
      font: 700 36px 'Roboto Condensed', sans-serif;
    }
    .sub { color: #d7e5f0; margin-top: 6px; }
    .qtr-section {
      background: #fff;
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 14px;
      margin-bottom: 14px;
    }
    .qtr-header {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
      padding-bottom: 10px;
      border-bottom: 1px solid #dde7ef;
      margin-bottom: 10px;
    }
    .qtr-badge {
      font: 700 11px 'Roboto Condensed', sans-serif;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      border-radius: 999px;
      padding: 4px 10px;
    }
    .qtr-badge.upcoming { background: #fef3d9; color: #7a5500; border: 1px solid #f4d487; }
    .qtr-badge.horizon { background: #e6f1fb; color: #0c447c; border: 1px solid #b8d6ef; }
    .qtr-label {
      font: 700 20px 'Roboto Condensed', sans-serif;
      color: var(--guardian);
    }
    .features { display: grid; gap: 10px; }
    .feat-card {
      border: 1px solid var(--border);
      border-left: 4px solid var(--guardian);
      border-radius: 8px;
      padding: 10px 12px;
      background: #fff;
    }
    .feat-card h4 {
      margin: 0;
      font: 700 20px 'Roboto Condensed', sans-serif;
      color: #0d3553;
    }
    .feat-card p {
      margin: 6px 0 0;
      color: #3f596d;
      font-size: 14px;
      line-height: 1.45;
    }
    .feat-tags { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 6px; }
    .tag {
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.03em;
      text-transform: uppercase;
      border-radius: 999px;
      padding: 2px 8px;
      border: 1px solid #d2e0eb;
      background: #f0f5f9;
      color: #1f465f;
    }
    footer {
      margin-top: 14px;
      color: #4b6273;
      font-size: 12px;
      text-align: center;
    }
    @media (max-width: 700px) {
      h1 { font-size: 30px; }
      .qtr-label { font-size: 18px; }
    }
  </style>
</head>
'''

# ---------------------------------------------------------------------------
# INTERNAL: release-row timeline, grouped by quarter, KPIs always visible
# ---------------------------------------------------------------------------

def kpi_block():
    cols = "".join(
        f'''<div class="kpi-column"><div class="kpi-period">{p}</div><div class="kpi-tbd">TBD</div></div>'''
        for p in ("30 Day", "60 Day", "90 Day")
    )
    return f'<div class="kpi-col kpi-visible"><div class="kpi-container">{cols}</div></div>'

def multi_note(feat):
    if feat.get("continues_to"):
        c = feat["continues_to"]
        return f'<span class="multi-note">&nbsp;&middot; planned {c["release"]} &rarr; {fmt_date(c["ship_date"])}</span>'
    if feat.get("started_in"):
        s = feat["started_in"]
        return f'<span class="multi-note">&nbsp;&middot; started {fmt_date(s["ship_date"])}</span>'
    return ""

def feature_html(feat):
    tags = "".join(f'<span class="tag tag-{t}">{TAG_LABELS.get(t, t.title())}</span>' for t in feat.get("tags", []))
    if feat.get("multi_sprint"):
        tags += '<span class="tag tag-multi">multi-sprint</span>'
    return f'''
            <div class="feature">
              <div class="feat-title">{feat["internal_title"]}{multi_note(feat)}</div>
              <div class="feat-value">{feat["internal_summary"]}</div>
              <div class="feat-meta">{tags}</div>
              {kpi_block()}
            </div>'''

def release_row_html(rel, is_last_in_quarter):
    status = rel["status"]
    feats = "".join(feature_html(f) for f in rel["features"])
    sprint_line = f'<div class="rel-num {status}">{rel["sprint_window"]}</div>' if rel.get("sprint_window") else ""
    label = {"shipped": "Shipped", "next": "Next", "upcoming": "Upcoming"}[status]
    line_cls = "tl-line hidden" if is_last_in_quarter else "tl-line"
    return f'''
        <div class="release-row">
          <div class="date-col">
            <div class="date-val {status}">{fmt_date(rel["ship_date"])}</div>
            <div class="rel-num {status}">{rel["release"]}</div>
            {sprint_line}
            <div class="status-label {status}">{label}</div>
          </div>
          <div class="tl-col">
            <div class="tl-dot {status}"></div>
            <div class="{line_cls}"></div>
          </div>
          <div class="feat-col">{feats}
          </div>
        </div><!-- /{rel["release"]} -->'''

def horizon_panel_html(h, tabkey, months):
    items = "".join(
        f'''
      <div class="empty-state">
        <div class="empty-title">{it["title"]}</div>
        <div class="empty-sub">{it["internal_summary"]}</div>
      </div>''' for it in h["items"]
    )
    return f'''
    <div class="qtr-panel" id="panel-{tabkey}" role="tabpanel">
      <div class="panel-header">
        <div>
          <div class="panel-title">{h["quarter"]} &mdash; {months}</div>
          <div class="panel-subtitle">{h["subtitle"]}</div>
        </div>
      </div>{items}
    </div>'''

QUARTER_MONTHS = {
    "Q2 2026": "April through June", "Q3 2026": "July through September",
    "Q4 2026": "October through December", "Q1 2027": "January through March",
    "Q2 2027": "April through June",
}
QUARTER_TABKEY = {"Q2 2026": "q2", "Q3 2026": "q3", "Q4 2026": "q4", "Q1 2027": "q1", "Q2 2027": "q2027"}

def build_internal_html():
    head = build_internal_head()

    dated_quarters = quarters_in_order(RELEASES, "quarter")
    horizon_quarters = [h["quarter"] for h in HORIZON]
    all_quarters = dated_quarters + horizon_quarters

    pairs = []
    for qi, q in enumerate(all_quarters):
        tabkey = QUARTER_TABKEY[q]
        tab = f'<button class="qtr-tab{" active" if qi == 0 else ""}" role="tab" data-qtr="{tabkey}">{q}</button>'

        if q in dated_quarters:
            q_releases = [r for r in RELEASES if r["quarter"] == q]
            rows = "".join(release_row_html(r, i == len(q_releases) - 1) for i, r in enumerate(q_releases))
            panel = f'''
    <div class="qtr-panel{" active" if qi == 0 else ""}" id="panel-{tabkey}" role="tabpanel">
      <div class="panel-header">
        <div><div class="panel-title">{q} &mdash; {QUARTER_MONTHS[q]}</div></div>
        <div class="legend">
          <div class="legend-item"><span class="legend-dot" style="background:var(--next-dot);box-shadow:0 0 0 2px var(--next-dot-ring);"></span> Next</div>
          <div class="legend-item"><span class="legend-dot" style="background:var(--upcoming-dot);"></span> Upcoming</div>
          <div class="legend-item"><span class="legend-dot" style="background:var(--shipped-dot);opacity:.7;"></span> Shipped</div>
        </div>
      </div>
      <div class="rows">{rows}
      </div>
    </div>'''
        else:
            h = next(h for h in HORIZON if h["quarter"] == q)
            panel = horizon_panel_html(h, tabkey, QUARTER_MONTHS[q])

        pairs.append((tab, panel))

    tabs, panels = zip(*pairs)

    last_updated = datetime.now().strftime("%m/%d/%y")

    body = f'''
<body>
  <div class="page">
    <div class="topbar">
      <svg width="319" height="100" viewBox="0 0 319 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <g clip-path="url(#logo-clip)">
          <path d="M205.828 57.4609C211.337 54.2739 214.618 49.0186 214.618 43.4044C214.618 33.4846 205.681 26.2874 193.378 26.2874H170.204V74.0291H185.892V54.675L199.33 74.0291H217.688L205.575 57.5876L205.828 57.4398V57.4609ZM196.848 45.6416C196.848 48.7653 194.009 51.298 190.539 51.298H185.64V38.2756H190.539C194.03 38.2756 196.848 40.8083 196.848 43.932V45.6416Z" fill="#ffffff" />
          <path d="M154.39 57.4609C159.9 54.2739 163.18 49.0186 163.18 43.4044C163.18 33.4846 154.243 26.2874 141.94 26.2874H118.766V74.0291H134.454V54.675L147.892 74.0291H166.25L154.138 57.5876L154.39 57.4398V57.4609ZM145.41 45.6416C145.41 48.7653 142.571 51.298 139.101 51.298H134.202V38.2756H139.101C142.592 38.2756 145.41 40.8083 145.41 43.932V45.6416Z" fill="#ffffff" />
          <path d="M68.2325 74.0291L81.7123 54.9282L95.1922 74.0291H110.712V26.2874H83.6891L50 74.0291H68.2325ZM94.372 36.9882V51.298H84.2779L94.372 36.9882Z" fill="#ffffff" />
          <path d="M247.487 25H240.526C228.666 25 219.013 34.6876 219.013 46.5914V53.4086C219.013 65.3124 228.666 75 240.526 75H247.487C259.348 75 269 65.3124 269 53.4086V46.5914C269 34.6876 259.348 25 247.487 25ZM252.597 51.699C252.597 56.1735 248.98 59.8248 244.501 59.8248H243.491C239.033 59.8248 235.395 56.1735 235.395 51.699V48.301C235.395 43.8265 239.033 40.1752 243.491 40.1752H244.501C248.959 40.1752 252.597 43.8265 252.597 48.301V51.699Z" fill="#ffffff" />
          <path d="M70.4616 26.0131H52.6918V51.0236H52.8179L70.4616 26.0131Z" fill="#97C459" />
        </g>
        <defs><clipPath id="logo-clip"><rect width="219" height="50" fill="white" transform="translate(50 25)" /></clipPath></defs>
      </svg>
      <div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
        <div style="font-size:11px;color:rgba(255,255,255,0.6);font-weight:600;letter-spacing:.04em;text-transform:uppercase;">Internal &middot; Full Detail</div>
        <button onclick="window.print()" style="padding:5px 14px;font-size:11px;font-family:inherit;cursor:pointer;border:0.5px solid rgba(255,255,255,0.25);border-radius:6px;background:rgba(255,255,255,0.08);color:rgba(255,255,255,0.75);font-weight:500;white-space:nowrap;transition:background .15s;" onmouseover="this.style.background='rgba(255,255,255,0.18)'" onmouseout="this.style.background='rgba(255,255,255,0.08)'">&#8681; Print to PDF</button>
        <div class="topbar-right">
          <div class="digest-label">Release Digest</div>
          <div class="last-updated">Last updated <span id="last-updated-date">{last_updated}</span></div>
        </div>
      </div>
    </div>

    <div class="qtr-nav" role="tablist">{"".join(tabs)}
    </div>
{"".join(panels)}
  </div><!-- /page -->

  <script>
    var tabs = document.querySelectorAll('.qtr-tab');
    var panels = document.querySelectorAll('.qtr-panel');
    tabs.forEach(function (tab) {{
      tab.addEventListener('click', function () {{
        var target = this.getAttribute('data-qtr');
        tabs.forEach(function (t) {{ t.classList.remove('active'); }});
        panels.forEach(function (p) {{ p.classList.remove('active'); }});
        this.classList.add('active');
        document.getElementById('panel-' + target).classList.add('active');
      }});
    }});
    document.body.classList.add('internal-view');
  </script>
</body>
</html>'''

    return head + body

# ---------------------------------------------------------------------------
# EXTERNAL: quarter-card sections, "both"-audience only, deduped per quarter
# ---------------------------------------------------------------------------

def render_tags(tag_list):
    if not tag_list:
        return ""
    spans = "".join(f'<span class="tag tag-{t}">{TAG_LABELS.get(t, t.title())}</span>' for t in tag_list)
    return f'<div class="feat-tags">{spans}</div>'

def build_external_html():
    head = build_external_head()

    sections = []

    dated_quarters = [q for q in quarters_in_order(RELEASES, "quarter") if q != "Q2 2026"]

    for q in dated_quarters:
        # Collapse every internal-release feature into one card per external_title.
        cards = {}
        for rel in RELEASES:
            if rel["quarter"] != q:
                continue
            for f in rel["features"]:
                if f.get("audience") != "both" or not f.get("external_title") or not f.get("external_summary"):
                    continue
                cards[f["external_title"]] = (f["external_summary"], f.get("external_tags", []))

        cards_html = "".join(
            f'<div class="feat-card"><h4>{title}</h4><p>{summary}</p>{render_tags(tags)}</div>'
            for title, (summary, tags) in cards.items()
        )
        status_cls, status_label = ("upcoming", "Planned") if q == "Q3 2026" else ("horizon", "Horizon")
        sections.append(f'''
    <div class="qtr-section">
      <div class="qtr-header">
        <span class="qtr-badge {status_cls}">{q} &middot; {status_label}</span>
        <span class="qtr-label">{q} &mdash; {QUARTER_MONTHS[q]}</span>
      </div>
      <div class="features">{cards_html}</div>
    </div>''')

    for h in HORIZON:
        cards_html = "".join(
            f'<div class="feat-card"><h4>{it["title"]}</h4><p>{it["external_summary"]}</p>{render_tags(it.get("external_tags", []))}</div>'
            for it in h["items"] if it.get("audience") == "both" and it.get("external_summary")
        )
        sections.append(f'''
    <div class="qtr-section">
      <div class="qtr-header">
        <span class="qtr-badge horizon">{h["quarter"]} &middot; Horizon</span>
        <span class="qtr-label">{h["quarter"]} &mdash; {QUARTER_MONTHS[h["quarter"]]}</span>
      </div>
      <div class="features">{cards_html}</div>
    </div>''')

    body = f'''
<body>
  <div class="page">
    <header>
      <h1>ARRO Product Roadmap</h1>
      <div class="sub">Planned capabilities across Q3 2026 through Q2 2027.</div>
    </header>
{"".join(sections)}
    <footer>ARRO Product Roadmap &middot; Q3 2026 &ndash; Q2 2027 &middot; Planned features and timing are subject to change. This roadmap reflects current intent and is not a contractual commitment.</footer>
  </div>
</body>
</html>'''
    return head + body

if __name__ == "__main__":
    internal_html = build_internal_html()
    external_html = build_external_html()

    INTERNAL_HTML_PATH.write_text(internal_html, encoding="utf-8")
    EXTERNAL_HTML_PATH.write_text(external_html, encoding="utf-8")

    print("Generated ARRO_roadmap.html and ARRO_Roadmap_External.html")