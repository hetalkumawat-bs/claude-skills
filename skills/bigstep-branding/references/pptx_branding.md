# BigStep branding in PowerPoint (python-pptx)

Full worked example: `examples/sample_pptx.py` (cover + content + closing,
rendered and verified). Use it as the template.

## Essentials
- 16:9 (`prs.slide_width=Inches(13.333); prs.slide_height=Inches(7.5)`).
- Fonts: use the SINGLE family `font.name="Poppins"` and set `font.bold=True`
  for headings/labels. Do NOT use weight-named families like "Poppins
  SemiBold"/"Poppins ExtraBold" — Word/PowerPoint can't resolve them unless
  installed as separate families, so they fall back. Install `assets/fonts/*.ttf`.
- Colors via `RGBColor(*bs.hx(bs.C.PRIMARY))`.
- Logos via `slide.shapes.add_picture(bs.logo_path(v), x, y, width=w,
  height=int(w*bs._ASPECT[v]))` — pass height to keep aspect.
- FLAT design — no shadows. `shadow.inherit=False` is NOT enough (the theme
  style ref still adds a drop shadow). For every autoshape, remove the
  `<p:style>` element AND append an empty `<a:effectLst/>` to `spPr` — see
  `flat()` in the example. Apply it to every rect/rounded/oval you create.

## Slide patterns (helpers defined in the example)
- **Cover/closing:** full blue rectangle bg; `rings(...)` ovals top-right (no
  fill, light-blue line); white logo; cyan accent bar; two-tone(white) title;
  bottom deep-blue chip bar (cover).
- **Content:** white bg; color logo top-left; light rule + short blue accent
  segment; right-aligned uppercase section label; `two_tone(...)` title with
  cyan underline; rounded stat cards (tint fill + colored left bar + ExtraBold
  value); rounded callout panel; footer (mark + website).
- **Tables:** header row `#1C62EC` + white SemiBold; zebra white/`#D4E6FF` (blue, no purple).

## Logo sizing & footer
- Large logo (~2.4in) ONLY on the cover/closing. Content/subpage headers use a
  small logo (~1.25in) — `content_header` in the example does this.
- Footer mark: size it to the text (~0.2in tall), vertically centre it on the
  website text, and keep it ~0.6in above the slide bottom so it is never
  clipped. See `footer()` in the example.

## Checklist
- [ ] Cover logo large; subpage logos small (~1.25in)
- [ ] Logo on every slide (white on blue, color on white)
- [ ] Footer mark sized to text, centred, clear bottom margin (never clipped)
- [ ] Poppins on every run; two-tone titles + cyan underline
- [ ] Stat cards / callouts as rounded shapes — not bullet walls
- [ ] Footer mark + `www.bigsteptech.com` on interior slides
- [ ] Cyan accents only; gold avoided
