import sys
sys.path.insert(0, "../scripts")
import bigstep_brand as bs
from bigstep_brand import C, FONT, BRAND, mm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table

bs.register_fonts()
PW, PH = A4
OUT = "/mnt/user-data/outputs/BigStep_Brand_Sample.pdf"
c = canvas.Canvas(OUT, pagesize=A4)


def para(c, text, x, y, w, font=FONT.REGULAR, size=10, leading=15, color=C.SLATE):
    c.setFillColor(bs.rl(color)); c.setFont(font, size)
    for ln in bs._wrap(text, font, size, w):
        c.drawString(x, y, ln); y -= leading
    return y


# ----------------------------------------------------------------- PAGE 1 cover
bs.cover_page(
    c, PW, PH,
    title="Capability & Engagement Overview",
    subtitle="A snapshot of how BigStep designs, builds, and scales AI-first, "
             "cloud-native products for enterprises and startups worldwide.",
    kicker="Company Profile  ·  2026",
    footer_chips=["AI & Gen AI", "Product Engineering", "Cloud & DevOps", "Data Engineering"],
)
c.showPage()

# ----------------------------------------------------------------- PAGE 2 summary
bs.page_frame(c, PW, PH, page_no=2, header_label="Executive Summary")
x = 18*mm
bs.two_tone(c, x, PH-42*mm, "Executive ", "Summary", size=22)
y = PH-52*mm
y = para(c,
    "BigStep Technologies is an AI-First, Cloud-Native software engineering and "
    "product development partner. We embed senior, cross-functional squads inside "
    "our clients' teams to ship resilient products faster — from first prototype to "
    "global scale. This overview summarises our footprint, the way we engage, and "
    "the outcomes our partners see.",
    x, y, PW-36*mm, leading=15)

# stat cards row
y -= 6*mm
cards = [("17+", "Years delivering software & AI"),
         ("700+", "Apps, products & solutions shipped"),
         ("500+", "Customers across 6+ industries")]
gap = 5*mm
cw = (PW-36*mm - 2*gap)/3
ch = 26*mm
for i, (v, l) in enumerate(cards):
    bs.stat_card(c, x+i*(cw+gap), y-ch, cw, ch, v, l,
                 accent=[C.PRIMARY, C.CYAN, C.PRIMARY][i])
y -= ch + 10*mm

# two-tone subhead + callout
bs.two_tone(c, x, y, "How We ", "Deliver", size=16)
y -= 9*mm
h = bs.callout(c, x, y, PW-36*mm, "Squad-as-a-Service",
    ["Dedicated, hand-picked teams — developers, designers, QA and DevOps — that "
     "work as an extension of your in-house team with shared ownership of outcomes.",
     "Scale up or down on demand, with deep domain expertise and a bias for action "
     "that surfaces risks early and keeps delivery predictable."],
    fill=C.TINT, accent=C.PRIMARY)
y -= h + 7*mm
bs.callout(c, x, y, PW-36*mm, "Proven Across Engagement Models",
    ["Staff augmentation, time & material, fixed-cost, global capability centre, or "
     "hybrid delivery — matched to your scope, timeline, and risk appetite."],
    fill=C.TINT, accent=C.CYAN)
c.showPage()

# ----------------------------------------------------------------- PAGE 3 divider
bs.section_divider(c, PW, PH, 1, "Engagement Snapshot")
c.showPage()

# ----------------------------------------------------------------- PAGE 4 details
bs.page_frame(c, PW, PH, page_no=4, header_label="Engagement Snapshot")
x = 18*mm
bs.two_tone(c, x, PH-42*mm, "Outcomes That ", "Compound", size=22)
y = PH-52*mm
y = para(c,
    "Representative results from recent partnerships. Figures are drawn from "
    "delivered programmes across PropTech, media streaming, and healthcare.",
    x, y, PW-36*mm, leading=15)

# branded table
y -= 4*mm
data = [["Programme", "Focus", "Headline Outcome"],
        ["VTS Rise", "PropTech platform", "Scaled the platform 5X"],
        ["Jio Media Stack", "Live streaming SDK", "-15% CPU, 500+ streams/channel"],
        ["House of Diagnostics", "Healthcare platform", "Major lift in online bookings"],
        ["Channelize.io", "Live video commerce", "70% serverless, faster scaling"],
        ["FitPass", "Healthtech voice + AI", "-60% manual documentation"]]
tbl = Table(data, colWidths=[42*mm, 46*mm, 86*mm])
tbl.setStyle(bs.branded_table_style())
tw, th = tbl.wrap(PW-36*mm, 200*mm)
tbl.drawOn(c, x, y-th)
y -= th + 10*mm

# normal-weight bullet list (demonstrates regular body text for list items)
bs.two_tone(c, x, y, "What Partners ", "Value", size=16)
y -= 9*mm
y = bs.bullet_list(c, x, y, [
    "Squads led by engineers and designers who have shipped at scale \u2014 not ramp-up resources",
    "Every deliverable carries a consistent, premium BigStep identity",
    "Transparent communication, weekly demos, and shared ownership of outcomes",
    "Deep domain expertise across PropTech, media, healthtech, and fintech",
], PW-36*mm)
c.showPage()

# ----------------------------------------------------------------- PAGE 5 closing
bs.closing_page(
    c, PW, PH,
    title=["Let's build", "your next big step."],
    contact={"title": "Contact Us",
             "lines": [BRAND["email"], BRAND["website"]],
             "meta": "Founded 2008  \u00b7  " + BRAND["hq"]})
c.showPage()

c.save()
print("saved", OUT)
