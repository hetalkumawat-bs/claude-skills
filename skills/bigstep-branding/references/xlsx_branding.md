# BigStep branding in Excel (openpyxl)

Full worked example: `examples/sample_xlsx.py` — 4 sheets, each with the SAME
branded header + footer, branded tables, a brand-blue chart, live formulas and
zero formula errors. Use it as the template. Pair with the `xlsx` skill for
mechanics and run its `scripts/recalc.py` to recalc + verify no errors.

## Consistency is the rule
Every sheet must look like the same document (this is what makes it
production-grade — don't leave data sheets bare):
- **Logo** top-left (anchored image at `B2`, ~34px tall).
- **Two-tone title** via rich text at `B4`: `CellRichText([TextBlock(InlineFont(
  rFont="Poppins", sz=18, b=True, color="041342"), "Lead "), TextBlock(
  InlineFont(... color="1C62EC"), "Tail")])`.
- **Cyan accent bar** under the title: anchor `assets/accent_cyan.png` at `B5`
  (set width ~42px, height ~5px). (`accent_primary.png` also ships.)
- **Section label** top-right, row 2, uppercase, muted `#6B7A8D`.
- **Faint rule**: thin `#E4F2FF` bottom border across the header row.
- **Footer** via the real page footer so it prints on every sheet:
  `ws.oddFooter.left.text='&"Poppins"&8&K6B7A8D www.bigsteptech.com'` and
  `ws.oddFooter.right.text='&"Poppins"&8&K6B7A8D Page &P of &N '`.

## Tables, KPIs, chart
- Branded table: header fill `#1C62EC` + white bold Poppins; body zebra white /
  `#D4E6FF` (BLUE — never lavender); thin `#E4F2FF` borders; wrap on; row height
  ~24 so wrapped cells don't clip.
- KPIs: a small "At a Glance" branded table (Metric | Value) — robust, unlike
  floating cards which overflow.
- Chart: brand-blue bars — `chart.series[0].graphicalProperties.solidFill =
  "1C62EC"`, `legend=None`, keep width ≲ the table's column span so it isn't
  clipped by the print area.

## Correctness
- Font `Poppins` on every written cell (Calibri fallback; Excel can't embed
  fonts). Gridlines off; column A as a ~2.4 gutter.
- Use Excel **formulas** (`=SUM(...)`) not Python-computed values; then recalc
  and confirm zero `#REF!/#DIV0!/#VALUE!` errors.
- Page setup so each sheet prints on one page wide:
  `page_setup.fitToWidth=1; fitToHeight=0; sheet_properties.pageSetUpPr=
  PageSetupProperties(fitToPage=True)`; set `ws.print_area` to the used range.

## Checklist
- [ ] Every sheet: logo + two-tone title + cyan accent + section label + footer
- [ ] Branded tables: blue header, blue `#D4E6FF` zebra, wrapped, no clipping
- [ ] Brand-blue chart, no legend, not clipped
- [ ] Poppins everywhere; gridlines off; A-column gutter
- [ ] Formulas (not hardcodes); zero errors after recalc
- [ ] fit-to-width + print_area so each sheet is one clean page
