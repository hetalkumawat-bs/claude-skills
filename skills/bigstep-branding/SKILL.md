---
name: bigstep-branding
description: >
  Apply BigStep Technologies' full visual identity to any deliverable Claude
  produces — Word documents, PowerPoint decks, PDFs, spreadsheets, and
  HTML/web. Use this skill WHENEVER you create a document, presentation,
  report, proposal, profile, case study, one-pager, or any client- or
  internal-facing artifact for BigStep, even if the user doesn't say
  "branding". This is a complete design system, not a logo stamp: it ships the
  exact brand typeface (Poppins, the font used in BigStep's deck and site), the
  exact palette, the logo in three variants, and ReportLab/Office primitives
  for the brand's design language — concentric-ring cover motif, two-tone
  titles with cyan underlines, stat cards, callout panels, section dividers,
  branded tables, and consistent header/footer bands. Also use when asked to
  "make it on-brand", "add our logo/template", "use our colours/fonts", or to
  restyle an existing file to look premium and CEO-ready.
---

# BigStep Branding — Design System

This skill makes BigStep deliverables look like they came from one studio:
premium, consistent, and unmistakably BigStep. It is a **design system**, not a
logo-on-text layer. Pair it with the format skill (`docx`, `pptx`, `pdf`,
`xlsx`, `frontend-design`) for mechanics; this supplies the brand layer.

## The non-negotiables (what makes it BigStep)

1. **Poppins everywhere.** Poppins is the brand typeface (it's literally the
   font embedded in the corporate deck). The six weights ship in
   `assets/fonts/`. In Office formats (docx/pptx) use the SINGLE family
   "Poppins" + bold for weight (weight-named families like "Poppins SemiBold"
   don’t resolve in Word and fall back). In PDF the module registers each
   weight as a real embedded TTF. Never substitute another face. Keep the
   design FLAT — no drop shadows in any format.
2. **Two-tone titles** — lead word(s) Deep Navy `#041342`, emphasis phrase
   BigStep Blue `#1C62EC`, with a short **cyan underline** beneath. White on
   blue/dark surfaces.
3. **Blue-only.** The whole system is blue / navy / cyan + neutrals. NEVER use
   purple or lavender. Panels & zebra rows use the two BLUE tints `#E4F2FF` and
   `#D4E6FF`.
4. **No grey header line.** Interior page headers use a short blue accent
   segment only. The full-width grey/tint rule is removed.
5. **The blue + rings system.** Covers, section dividers and closing pages are
   full-bleed `#1C62EC` with the faint **concentric-ring motif** in a corner
   and the white logo. Interior pages are white with a header band (logo +
   accent rule) and a footer (mark + `www.bigsteptech.com` + page no.).
6. **Designed components, not paragraphs.** Use stat cards, callout panels
   (rounded, tinted, colored left rule), label chips, and branded tables
   (blue header row, blue `#D4E6FF` zebra) — see the primitives below.
7. **Logo on every page/slide**, every format. Color on light, white on dark,
   mark for tight spots.
8. **Bullets are body text.** List items use the same Poppins Regular / slate /
   10–11pt as body copy. They are NEVER bold or emphasised. Only component
   titles (callout title, card title, table header) may be bold.
9. **Embed the font in Word.** Poppins falls back to Calibri in Word if not
   installed, so .docx output embeds the TTFs (see `scripts/embed_fonts.py`).
   PDF embeds fonts inherently; pptx/xlsx rely on the bundled TTFs being
   installed (Calibri fallback).

## How to build (PDF — full design control)

`scripts/bigstep_brand.py` is the engine. It exposes the palette, fonts, logo
loader, and ReportLab primitives.

```python
import sys; sys.path.insert(0, "<skill>/scripts")
import bigstep_brand as bs
bs.register_fonts()                       # registers Poppins with ReportLab
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
c = canvas.Canvas("out.pdf", pagesize=A4); PW, PH = A4

bs.cover_page(c, PW, PH, title="...", subtitle="...", kicker="...",
              footer_chips=["AI & Gen AI", "Product Engineering", ...]); c.showPage()
bs.page_frame(c, PW, PH, page_no=2, header_label="Executive Summary")
bs.two_tone(c, 18*bs.mm, PH-42*bs.mm, "Executive ", "Summary", size=22)
bs.stat_card(c, x, y, w, h, "700+", "Apps & solutions shipped")
bs.callout(c, x, y, w, "Squad-as-a-Service", ["..."], fill=bs.C.TINT)
# branded table: Table(...).setStyle(bs.branded_table_style())
bs.section_divider(c, PW, PH, 1, "Engagement Snapshot"); c.showPage()
bs.closing_page(c, PW, PH, ["Let's build", "your next big step."],
               contact={"title":"Contact Us","lines":[...]})  # accent ABOVE title
c.save()
```

**Always use `bs.draw_logo(...)`** for logos in ReportLab — never bare
`drawImage` with only a width (it mis-positions the image; the helper passes
explicit width+height and flattens transparency so it always renders).

A complete, working reference deck is in `examples/sample_pdf.py` — read it
first; it composes every primitive into a CEO-ready document.

## How to build (PowerPoint & Word)

Slides and docs use the same palette, fonts, logo, two-tone titles, stat
cards, callout panels, and branded tables — rebuilt with native shapes/tables.
Working, rendered references:
- `examples/sample_pptx.py` — cover, content (stat cards + callout), closing.
- `examples/sample_docx.py` — header band, stat cards, callout, branded table.

Set fonts to the family name `Poppins` (install `assets/fonts/*.ttf` on the
machine that opens the file) with `Calibri` as the only fallback. Detailed
recipes: `references/pptx_branding.md`, `references/docx_branding.md`,
`references/pdf_branding.md`.

## Reference files

- `references/brand_guidelines.md` — canonical palette, type scale, logo rules,
  component specs, voice. **Read this first.**
- `references/{pdf,pptx,docx,xlsx}_branding.md` — per-format recipes + checklists.

## Palette (exact, sampled from the deck)

`#1C62EC` primary blue · `#0F3FA6` deep blue (depth) · `#3FC7F2` cyan accent ·
`#041342` heading navy · `#2B3D4F` body slate · `#E4F2FF` light tint ·
`#D4E6FF` blue tint 2 (zebra) · `#FDCA0E` gold (rare) · `#FFFFFF` white · `#6B7A8D` muted.

## Assets

- `assets/bigstep_logo_color.png` / `_white.png` / `bigstep_mark.png`
- `assets/fonts/Poppins-*.ttf` (+ `OFL.txt` license)

## Companion skill

`tech-doc` builds a technical documentation deliverable end to end — the section outline, the
evidence rules, and a markdown → branded DOCX → PDF pipeline that already carries these styles.
Use it for the document; use this skill for the design layer around it.
