# BigStep branding in PDF (ReportLab)

The engine is `scripts/bigstep_brand.py`; the full worked example is
`examples/sample_pdf.py` (read it — it builds a 5-page CEO-ready deck).

## Setup
```python
import sys; sys.path.insert(0, "<skill>/scripts")
import bigstep_brand as bs
bs.register_fonts()                 # Poppins -> ReportLab (call once)
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
c = canvas.Canvas("out.pdf", pagesize=A4); PW, PH = A4
```

## Primitives (all take the canvas `c`)
- `bs.cover_page(c, PW, PH, title, subtitle=, kicker=, footer_chips=[...])`
- `bs.section_divider(c, PW, PH, number, title)`
- `bs.closing_page(c, PW, PH, title, subtitle=, contact={title,lines,meta})` —
  blue hero/closing; accent sits ABOVE the title block (multi-line safe)
- `bs.page_frame(c, PW, PH, page_no=, header_label=)`  — header+footer+rings
- `bs.two_tone(c, x, y, lead, tail, size=, on_dark=False)`  — title + cyan rule
- `bs.stat_card(c, x, y, w, h, value, label, accent=)`
- `bs.callout(c, x, y, w, title, [lines], fill=, accent=, pad=)` → returns height
- `bs.chip(c, x, y, text)` ; `bs.concentric(c, cx, cy, color, ...)`
- `bs.bullet_list(c, x, y, items, w)` — normal-weight body-text bullets
- `bs.branded_table_style()` → TableStyle for a reportlab `Table`
- `bs.draw_logo(c, variant, x, y, width, matte=)` — ALWAYS use this for logos

## Logo rule (never cut off)
The footer mark is sized by HEIGHT (~3.6mm) and vertically centred on the
website text — never by width (it's a tall shape). Large logo only on
cover/section/closing; interior pages use the compact ~22mm header logo.
Never call `c.drawImage` on a logo with only a width — it mis-positions and may
render blank. `bs.draw_logo` passes explicit width+height and flattens alpha.

## Page recipe
1. Cover → `cover_page`, `showPage()`.
2. Interior → `page_frame(...)`, then `two_tone(...)` title, body via wrapped
   text, then `stat_card`/`callout`/branded `Table`.
3. Section break → `section_divider`. Closing → blue bg + rings + white logo +
   two-tone(white) + white contact card (see example).

## Accent placement (avoid overlapping borders)
The cyan accent bar must never sit between title lines. For hero/closing
titles use `closing_page` (accent above the whole block). For single-line
content headings, `two_tone` draws the underline safely BELOW the baseline.
Never hand-place an accent rect between two text lines.

## Footer mark
The footer mark is sized to the website text and vertically centred on it, with
a clear bottom margin (`_footer` uses baseline 13mm) so the logo is never
clipped or oversized.

## Checklist
- [ ] Poppins registered; navy headings, slate body
- [ ] Cover/section/closing full-bleed `#1C62EC` + rings + white logo
- [ ] Interior pages: color logo + accent rule header; mark+website+page footer
- [ ] Two-tone titles with cyan underline; hero titles via closing_page
      (accent ABOVE the block — never overlapping text)
- [ ] Bullet lists via `bullet_list` (Poppins Regular, never bold)
- [ ] Components (cards/callouts/branded tables) — not plain paragraphs
- [ ] Cyan accents only; gold avoided
