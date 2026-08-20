# BigStep branding in Word (python-docx)

Full worked example: `examples/sample_docx.py` (header band, stat cards,
callout, branded table — rendered and verified). Use it as the template.

## Essentials
- Use the SINGLE family `Poppins` with `bold=True` for weight. Do NOT use
  "Poppins SemiBold"/"ExtraBold"/"Medium" as font names — a standard Poppins
  install exposes those as styles, not families, so Word falls back to Calibri.
- Set the font in THREE places so Word always honors it: docDefaults
  (`w:docDefaults/w:rPrDefault`), the `Normal` style, and each run’s `w:rFonts`
  (ascii/hAnsi/cs/eastAsia). See `set_doc_default_font()` + `set_font()` in the
  example. Install `assets/fonts/*.ttf`. Fallback: Calibri only.
- Tables/cards are FLAT (no shadows) by nature — keep it that way.
- Header: `section.header` first paragraph → `add_picture(logo_path("color"),
  width=Inches(1.5))`; add a thin bottom paragraph border in `#E4F2FF` as the
  header rule. Footer: website in Medium 8pt muted.
- Two-tone title: two runs (navy lead + blue tail) in Poppins ExtraBold.
- Accent rule / stat cards / callouts: borderless shaded tables with cell
  `w:shd` fills and a thick colored LEFT `w:tcBorders` as the accent rule, plus
  `w:tcMar` padding (helpers in the example).
- Branded table: header cells shaded `#1C62EC` + white SemiBold; body rows
  zebra white/`#D4E6FF`; thin `#E4F2FF` grid.


## Embed the font (so Poppins holds in Word without a local install)
Word falls back to Calibri if Poppins isn't installed on the reader's machine.
Embed the TTFs into the .docx after saving:
```python
from embed_fonts import embed_fonts_in_docx
doc.save(path)
embed_fonts_in_docx(path, [{"name":"Poppins",
    "regular": ".../Poppins-Regular.ttf", "bold": ".../Poppins-Bold.ttf"}])
```
This obfuscates the TTFs to .odttf, wires up fontTable/rels/content-types, and
sets `<w:embedTrueTypeFonts/>` — so Word renders Poppins everywhere. See
`scripts/embed_fonts.py` and `examples/sample_docx.py`.

## Bullet lists
Use the `bullets(doc, items)` helper. It applies the List Bullet style with
bold=False, Poppins Regular, slate, 10.5pt — matching body paragraphs exactly.
Never set bold on list items; only component titles (callout, card, table
header) are bold.

## Checklist
- [ ] Color logo in header + thin rule; website footer
- [ ] Poppins TTFs EMBEDDED via embed_fonts_in_docx (holds without install)
- [ ] Poppins via run fonts AND `w:rFonts`; navy headings, slate body
- [ ] Two-tone title; designed stat cards + callout panels
- [ ] Bullet lists in normal body weight (never bold)
- [ ] Branded table (blue header, BLUE `#D4E6FF` zebra — no purple)
- [ ] Cyan accents only; gold avoided
