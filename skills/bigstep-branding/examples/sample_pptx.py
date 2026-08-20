"""BigStep branded PPTX — 6 slides, flat (no shadows), blue-only, Poppins+bold."""
import sys, os
sys.path.insert(0, "../scripts")
import bigstep_brand as bs
from bigstep_brand import C, BRAND
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml

def C_(h): return RGBColor(*bs.hx(h))
POP = "Poppins"
_A = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'

prs = Presentation()
prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
SW, SH = prs.slide_width, prs.slide_height
BLANK = prs.slide_layouts[6]

def flat(shape):
    sp = shape._element; spPr = sp.spPr
    if spPr is not None:
        for el in list(spPr):
            if el.tag.endswith('}effectLst') or el.tag.endswith('}effectDag'):
                spPr.remove(el)
        spPr.append(parse_xml(f'<a:effectLst {_A}/>'))
    style = sp.find('{http://schemas.openxmlformats.org/presentationml/2006/main}style')
    if style is not None: sp.remove(style)
    return shape

def no_line(sp): sp.line.fill.background()
def fill(sp, h): sp.fill.solid(); sp.fill.fore_color.rgb = C_(h); no_line(sp)

def rect(slide, x, y, w, h, hexc, rounded=False, radius=0.08):
    shp = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE, x, y, w, h)
    fill(shp, hexc)
    if rounded:
        try: shp.adjustments[0] = radius
        except Exception: pass
    return flat(shp)

def ring(slide, cx, cy, d, hexc):
    o = slide.shapes.add_shape(MSO_SHAPE.OVAL, int(cx-d/2), int(cy-d/2), int(d), int(d))
    o.fill.background(); o.line.color.rgb = C_(hexc); o.line.width = Pt(1.0)
    return flat(o)

def rings(slide, cx, cy, hexc, start=1.4, step=1.2, n=7):
    for i in range(n): ring(slide, cx, cy, Inches(start+i*step), hexc)

def text(slide, x, y, w, h, runs, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, ls=1.05, sa=0):
    tb = slide.shapes.add_textbox(x, y, w, h); tf = tb.text_frame
    tf.word_wrap = True; tf.vertical_anchor = anchor
    for m in ('margin_left','margin_right','margin_top','margin_bottom'): setattr(tf, m, 0)
    first = True
    for line in runs:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        p.alignment = align; p.line_spacing = ls
        if sa: p.space_after = Pt(sa)
        for (t, sz, col, bold) in line:
            r = p.add_run(); r.text = t; r.font.name = POP; r.font.size = Pt(sz); r.font.color.rgb = C_(col); r.font.bold = bold
    return tb

def logo(slide, variant, x, y, w):
    slide.shapes.add_picture(bs.logo_path(variant), x, y, width=w, height=int(w*bs._ASPECT[variant]))

def footer(slide, on_dark=False, page=None):
    col = C.WHITE if on_dark else C.MUTED
    # footer row sits ~0.55in above the slide bottom (clear margin); the mark is
    # sized to the text and vertically centred so it is never oversized/clipped.
    base_y = SH - Inches(0.62)
    mark_h = Inches(0.17); mark_w = int(mark_h / bs._ASPECT["mark"])
    row_h = Inches(0.34)
    # vertically centre the mark within the footer text row
    mark_y = base_y + int((row_h - mark_h) / 2)
    slide.shapes.add_picture(bs.logo_path("mark"), Inches(0.6), mark_y, width=mark_w, height=mark_h)
    text(slide, Inches(0.6)+mark_w+Inches(0.08), base_y, Inches(5), row_h,
         [[(BRAND["website"], 9, col, False)]], anchor=MSO_ANCHOR.MIDDLE)
    if page is not None:
        text(slide, SW-Inches(1.2), base_y, Inches(0.6), row_h,
             [[(f"{page:02d}", 9, col, False)]], align=PP_ALIGN.RIGHT, anchor=MSO_ANCHOR.MIDDLE)

def content_header(slide, lead, tail, label, page):
    rect(slide, 0, 0, SW, SH, C.WHITE)
    rings(slide, SW-Inches(0.1), Inches(0.1), C.RING, start=1.0, step=1.0, n=5)
    # subpage logo is small — the large logo is reserved for the cover slide
    logo(slide, "color", Inches(0.55), Inches(0.35), Inches(0.85))
    text(slide, Inches(8), Inches(0.45), Inches(4.7), Inches(0.3), [[(label.upper(), 9.5, C.MUTED, True)]], align=PP_ALIGN.RIGHT)
    # blue accent segment only — no grey line
    pass  # no line below logo
    text(slide, Inches(0.55), Inches(1.15), SW-Inches(1.1), Inches(0.85),
         [[(lead, 28, C.NAVY, True), (tail, 28, C.PRIMARY, True)]])
    uw = min(Inches(len(lead+tail)*0.22), Inches(6.5))
    rect(slide, Inches(0.57), Inches(1.92), uw, Inches(0.05), C.PRIMARY)
    footer(slide, page=page)

def card(slide, x, y, w, h, title, body, accent):
    rect(slide, x, y, w, h, C.TINT, rounded=True, radius=0.06)
    rect(slide, x, y, Inches(0.09), h, accent)
    text(slide, x+Inches(0.35), y+Inches(0.22), w-Inches(0.55), Inches(0.5), [[(title, 15, C.NAVY, True)]])
    text(slide, x+Inches(0.35), y+Inches(0.72), w-Inches(0.55), h-Inches(0.9), [[(body, 11.5, C.SLATE, False)]], ls=1.2)

def set_cell(cell, txt, size, color, bold):
    cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    cell.margin_left = Inches(0.16); cell.margin_right = Inches(0.1)
    cell.margin_top = Inches(0.04); cell.margin_bottom = Inches(0.04)
    tf = cell.text_frame; p = tf.paragraphs[0]
    r = p.add_run(); r.text = txt; r.font.name = POP; r.font.size = Pt(size); r.font.color.rgb = C_(color); r.font.bold = bold

def branded_table(slide, x, y, w, headers, rows, ratios, rowh=0.55):
    nrows = len(rows)+1; ncols = len(headers)
    gf = slide.shapes.add_table(nrows, ncols, x, y, w, Inches(rowh*nrows))
    tbl = gf.table; tbl.first_row = False; tbl.horz_banding = False
    total = sum(ratios)
    for j, rt in enumerate(ratios): tbl.columns[j].width = int(w*rt/total)
    for i in range(nrows): tbl.rows[i].height = Inches(rowh)
    for j, h in enumerate(headers):
        c = tbl.cell(0, j); c.fill.solid(); c.fill.fore_color.rgb = C_(C.PRIMARY)
        set_cell(c, h, 11, C.WHITE, True)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = tbl.cell(i+1, j); c.fill.solid(); c.fill.fore_color.rgb = C_(C.WHITE if i % 2 == 0 else C.TINT2)
            set_cell(c, val, 10.5, C.SLATE, False)
    return gf

def bullet_list(slide, x, y, w, items, size=11, ls=1.3):
    """Normal-weight body-text bullet list. Items are Poppins Regular, slate,
    and NEVER bold — matching body paragraph style exactly."""
    runs = []
    for item in items:
        runs.append([("\u2022  " + item, size, C.SLATE, False)])
    return text(slide, x, y, w, Inches(len(items) * 0.36), runs, ls=ls)

ICONS = str(bs.ASSETS / "icons")
def icon(slide, x, y, size, name, variant="primary"):
    """Place a proper Lucide line icon (PNG) on the slide."""
    import os; path = f"{ICONS}/{variant}/{name}.png"
    if os.path.exists(path):
        slide.shapes.add_picture(path, x, y, width=size, height=size)

# 1 — cover
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, C.PRIMARY)
rings(s, SW-Inches(0.2), Inches(0.2), C.RING_ON_BLUE)
logo(s, "white", Inches(0.6), Inches(0.55), Inches(2.4))
rect(s, Inches(0.62), Inches(3.0), Inches(1.4), Inches(0.13), C.CYAN)
text(s, Inches(0.6), Inches(2.5), Inches(8), Inches(0.4), [[("COMPANY PROFILE  \u00b7  2026", 13, C.CYAN, True)]])
text(s, Inches(0.6), Inches(3.3), Inches(9.5), Inches(2),
     [[("Capability & ", 46, C.WHITE, True)], [("Engagement Overview", 46, C.WHITE, True)]], ls=1.02)
text(s, Inches(0.62), Inches(5.4), Inches(8), Inches(1),
     [[("A snapshot of how BigStep designs, builds, and scales AI-first,", 15, "#D9E6FF", False)],
      [("cloud-native products for enterprises and startups worldwide.", 15, "#D9E6FF", False)]], ls=1.25)
rect(s, 0, SH-Inches(0.62), SW, Inches(0.62), C.PRIMARY_D)
text(s, 0, SH-Inches(0.62), SW, Inches(0.62),
     [[("AI & Gen AI      |      Product Engineering      |      Cloud & DevOps      |      Data Engineering", 11, C.WHITE, False)]],
     align=PP_ALIGN.CENTER, anchor=MSO_ANCHOR.MIDDLE)

# 2 — executive summary
s = prs.slides.add_slide(BLANK)
content_header(s, "Executive ", "Summary", "Executive Summary", 2)
text(s, Inches(0.6), Inches(2.7), SW-Inches(1.2), Inches(0.9),
     [[("BigStep embeds senior, cross-functional squads inside your team to ship resilient, "
        "cloud-native products faster \u2014 from first prototype to global scale.", 13, C.SLATE, False)]], ls=1.3)
cards = [("17+", "Years delivering software & AI", C.PRIMARY),
         ("700+", "Apps, products & solutions shipped", C.CYAN),
         ("500+", "Customers across 6+ industries", C.PRIMARY)]
cw = Inches(3.85); ch = Inches(1.4); gap = Inches(0.32); x0 = Inches(0.6); y0 = Inches(3.85)
for i, (v, l, a) in enumerate(cards):
    x = x0 + i*(cw+gap)
    rect(s, x, y0, cw, ch, C.TINT, rounded=True, radius=0.09)
    rect(s, x, y0, Inches(0.09), ch, a)
    text(s, x+Inches(0.35), y0+Inches(0.16), cw-Inches(0.5), Inches(0.6), [[(v, 26, C.NAVY, True)]])
    text(s, x+Inches(0.35), y0+Inches(0.76), cw-Inches(0.5), Inches(0.6), [[(l, 11, C.SLATE, False)]], ls=1.1)
co_y = Inches(5.6)
rect(s, Inches(0.6), co_y, SW-Inches(1.2), Inches(1.15), C.TINT, rounded=True, radius=0.06)
rect(s, Inches(0.6), co_y, Inches(0.1), Inches(1.15), C.PRIMARY)
text(s, Inches(1.0), co_y+Inches(0.16), SW-Inches(2), Inches(0.4), [[("Squad-as-a-Service", 14, C.NAVY, True)]])
text(s, Inches(1.0), co_y+Inches(0.58), SW-Inches(2.0), Inches(0.5),
     [[("Dedicated, hand-picked developers, designers, QA and DevOps that work as an extension of "
        "your in-house team \u2014 scaling up or down on demand.", 11.5, C.SLATE, False)]], ls=1.2)
footer(s, page=2)

# 3 — core services (2x2 cards)
s = prs.slides.add_slide(BLANK)
content_header(s, "Our Core ", "Services", "Capabilities", 3)
items = [("Digital Products", "Product development, web & mobile apps,\nbackend engineering, and QA.", C.PRIMARY, "monitor"),
         ("Artificial Intelligence", "Generative AI, agentic AI, and applied ML\nacross your workflows.", C.CYAN, "sparkles"),
         ("Data Solutions", "Data engineering, modernization, and analytics\nthat compound over time.", C.CYAN, "database"),
         ("Cloud & DevOps", "Cloud architecture, managed services, CI/CD,\nand infra modernization.", C.PRIMARY, "cloud")]
cw = Inches(5.95); ch = Inches(1.85); gx = Inches(0.45); gy = Inches(0.4); x0 = Inches(0.6); y0 = Inches(2.9)
ico_sz = Inches(0.32)
for i, (t, b, a, ico_name) in enumerate(items):
    x = x0 + (i % 2)*(cw+gx); y = y0 + (i//2)*(ch+gy)
    rect(s, x, y, cw, ch, C.TINT, rounded=True, radius=0.06)
    rect(s, x, y, Inches(0.09), ch, a)
    v = "primary" if a == C.PRIMARY else "cyan"
    icon(s, x+Inches(0.28), y+Inches(0.2), ico_sz, ico_name, v)
    text(s, x+Inches(0.72), y+Inches(0.18), cw-Inches(0.9), Inches(0.4), [[(t, 15, C.NAVY, True)]])
    text(s, x+Inches(0.72), y+Inches(0.7), cw-Inches(0.9), Inches(1.0), [[(b, 11.5, C.SLATE, False)]], ls=1.2)
footer(s, page=3)

# 4 — what partners value (bullet list — normal body weight, never bold)
s = prs.slides.add_slide(BLANK)
content_header(s, "What Partners ", "Value", "Our Promise", 4)
text(s, Inches(0.6), Inches(2.7), SW-Inches(1.2), Inches(0.8),
     [[("Everything below is body text weight — Poppins Regular, not bold.", 13, C.SLATE, False),]],
     ls=1.3)
bullet_list(s, Inches(0.6), Inches(3.5), SW-Inches(1.2), [
    "Squads led by engineers and designers who have shipped at scale — not ramp-up resources",
    "Every deliverable carries a consistent, premium BigStep identity",
    "Transparent communication, weekly demos, and shared ownership of outcomes",
    "Deep domain expertise across PropTech, media, healthtech, and fintech",
    "Agentic workflows, data extraction, and document intelligence",
    "Live video, media streaming, SaaS architecture, and cloud migration",
], size=12)
footer(s, page=5)

# 6 — outcomes (table)
s = prs.slides.add_slide(BLANK)
content_header(s, "Outcomes That ", "Compound", "Case Studies", 5)
branded_table(s, Inches(0.6), Inches(2.9), SW-Inches(1.2),
    ["Programme", "Focus", "Headline Outcome"],
    [["VTS Rise", "PropTech platform", "Scaled the platform 5X"],
     ["Jio Media Stack", "Live streaming SDK", "-15% CPU, 500+ streams/channel"],
     ["House of Diagnostics", "Healthcare platform", "Major lift in online bookings"],
     ["Channelize.io", "Live video commerce", "70% serverless, faster scaling"],
     ["FitPass", "Healthtech voice + AI", "-60% manual documentation"]],
    [3, 3, 4], rowh=0.62)
footer(s, page=4)

def bullet_list(slide, x, y, w, items, size=12, ls=1.3):
    """Normal-weight body-text bullet list for slides. Items are Poppins Regular,
    slate — NEVER bold. Bullets match the body paragraph style exactly."""
    runs = []
    for item in items:
        runs.append([("\u2022  " + item, size, C.SLATE, False)])
    return text(slide, x, y, w, Inches(len(items) * 0.36), runs, ls=ls)

# 5 — engagement models (table + bullet list)
s = prs.slides.add_slide(BLANK)
content_header(s, "Engagement ", "Models", "How We Engage", 6)
branded_table(s, Inches(0.6), Inches(2.9), SW-Inches(1.2),
    ["Model", "What it is", "Best for"],
    [["Staff Augmentation", "Add skilled engineers to your existing team", "Faster product delivery"],
     ["Time & Material", "Billing based on actual time & effort", "Evolving, iterative work"],
     ["Global Capability Centre", "A long-term dedicated team", "Multi-year scaling"],
     ["Fixed Cost", "Defined scope, timeline & budget", "Well-defined projects"],
     ["Hybrid Delivery", "Coordinated teams across locations", "Speed + cost efficiency"]],
    [3, 5, 3], rowh=0.55)
footer(s, page=6)

# 7 — closing
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, SW, SH, C.PRIMARY)
rings(s, SW-Inches(0.2), Inches(0.2), C.RING_ON_BLUE)
logo(s, "white", Inches(0.6), Inches(0.55), Inches(2.6))
rect(s, Inches(0.62), Inches(2.7), Inches(1.4), Inches(0.13), C.CYAN)
text(s, Inches(0.6), Inches(2.95), Inches(11), Inches(1.6),
     [[("Let's build", 50, C.WHITE, True)], [("your next big step.", 50, C.WHITE, True)]], ls=1.02)
cardw, cardh = Inches(7.6), Inches(1.5)
rect(s, Inches(0.6), Inches(5.2), cardw, cardh, C.WHITE, rounded=True, radius=0.08)
rect(s, Inches(0.6), Inches(5.2), Inches(0.1), cardh, C.CYAN)
text(s, Inches(1.0), Inches(5.4), Inches(5), Inches(0.4), [[("Contact Us", 15, C.NAVY, True)]])
text(s, Inches(1.0), Inches(5.85), Inches(6), Inches(0.7),
     [[(BRAND["email"], 12, C.SLATE, False)], [(BRAND["website"], 12, C.SLATE, False)]], ls=1.2)
footer(s, on_dark=True)

out = os.environ.get("OUT", "/mnt/user-data/outputs/BigStep_Brand_Sample.pptx")
prs.save(out); print("saved", out)
