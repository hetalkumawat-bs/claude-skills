# BigStep Brand Guidelines (canonical)

Derived from BigStep's official Corporate Profile. When in doubt, follow this
file — consistency is the point.

## 1. Logo
Three assets in `assets/`:
- `bigstep_logo_color.png` — navy + cyan wordmark → light backgrounds.
- `bigstep_logo_white.png` — all-white wordmark → blue/dark backgrounds.
- `bigstep_mark.png` — cyan ribbon mark → footers, tight spots, favicons.

Top-left on the first page and on every slide/master. Clear space ≥ the height
of the "b". Never recolor, stretch, rotate, shadow, or place the color logo on
a dark/busy background. Min wordmark width ≈ 1.1 in / 110 px.

**Logo sizing:** large wordmark ONLY on the cover / hero / closing (full-bleed
blue) pages. On interior/content pages and slides use a SMALL wordmark
(~16 mm PDF, ~0.7 in DOCX, ~0.85 in PPTX). **Footer mark:** size it by HEIGHT (~3.6 mm PDF /
~0.17 in PPTX) and vertically centre it on the website text — never size the
mark by width (it is a tall shape and would tower over the text or clip at the
page edge). Always pass explicit width AND height so a logo is never cut off.

## 2. Color palette (exact hex)
| Role | Hex | Use |
|------|-----|-----|
| Primary blue | `#1C62EC` | cover/section fills, bars, table headers, accents, CTAs |
| Deep blue | `#0F3FA6` | depth: chip bars, ghost numbers, gradients |
| Cyan accent | `#3FC7F2` | logo accent; underlines & small marks ONLY |
| Heading navy | `#041342` | titles & headings on light |
| Body slate | `#2B3D4F` | body copy, table text |
| Light tint | `#E4F2FF` | panels, stat cards, table header (light variant) |
| Blue tint 2 | `#D4E6FF` | alternating panels, zebra rows (deeper blue) |
| Ring (light) | `#EAF1FE` | concentric motif on white |
| Ring (blue) | `#3E7BEF` | concentric motif on blue |
| Gold | `#FDCA0E` | rare highlight only |
| White | `#FFFFFF` | default page/slide bg |
| Muted | `#6B7A8D` | captions, footer |

BLUE-ONLY rule: the entire palette is blue/navy/cyan + neutrals. NEVER use
purple/lavender. Panels and zebra rows use the two BLUE tints (`#E4F2FF`,
`#D4E6FF`). Rules: white is the default interior background; full-bleed `#1C62EC` is for
cover / section / closing only. Cyan is an accent, never a large fill. Gold is
reserved for a single highlight, never a theme color. Never invent shades.

## 3. Typography — Poppins (the brand face)
Poppins is the exact font embedded in the deck and used on the site. Ship/
install `assets/fonts/Poppins-*.ttf`. Fallback: Calibri only.

Type scale (PDF/print): Cover title 34–46 ExtraBold · Page title 22 Bold ·
Subhead 14–16 Bold · Section label/chip 10–12 SemiBold · Body 9.5–11 Regular ·
Caption/footer 8–9 Medium. Headings navy; body slate. Body line spacing ~1.3.

## 4. Signature heading device
Two-tone: lead word(s) navy `#041342`, emphasis phrase blue `#1C62EC`, with a
~16 mm cyan underline bar beneath the baseline. On blue/dark: all white.

## 5. Header line
No line below the logo. The underline goes under the page heading and matches
the heading text width. Interior pages have a clean, minimal header. There is NO
full-width grey/tint line — the blue accent is the sole rule. This applies
to PDF `page_frame`, PPTX `content_header`, and the DOCX header band.

## 6. Layout system
- **Cover / section / closing:** full-bleed `#1C62EC`; faint concentric rings
  in a corner; white logo; cyan accent bar; large two-tone(white) title;
  optional bottom deep-blue chip bar (service tags).
- **Section divider:** add a huge `#0F3FA6` ghost number behind the title.
- **Interior page:** white; header = color logo top-left + light rule with a
  short blue accent segment + optional right-aligned uppercase section label;
  footer = mark + `www.bigsteptech.com` + page number, all muted.

## 7. Components
- **Stat card:** rounded `#E4F2FF` panel, colored left rule (`#1C62EC`/`#3FC7F2`),
  ExtraBold navy value, Medium slate label.
- **Callout panel:** rounded tinted panel (`#E4F2FF`; deeper `#D4E6FF` for an
  alternate), colored left
  rule, SemiBold navy title, Regular slate body. Alternate the two tints.
- **Label chip:** small rounded `#E4F2FF` pill, SemiBold navy text.
- **Branded table:** header row `#1C62EC` + white SemiBold; body slate Regular;
  zebra white / `#D4E6FF`; thin `#E4F2FF` grid; generous padding.

## 9. Icons (shapes as pictograms)
Use small accent-colored auto-shapes from `MSO_SHAPE` as inline pictogram
icons next to card titles and stat values. They add visual identity without
importing external icon fonts. Rules:
- Small (~0.25–0.3 in), filled with the card's accent color, flat (no shadow).
- Positioned inside the card, left of the title or top-right of a stat panel.
- Use sparingly — cards and stat panels only, never on every bullet or heading.
- Good shapes: `GEAR_6` (system/engine), `LIGHTNING_BOLT` (AI/speed),
  `CLOUD` (cloud), `FLOWCHART_DOCUMENT` (docs), `FLOWCHART_DATA` (data),
  `CUBE` (package), `STAR_4_POINT` (highlight), `FLOWCHART_DISPLAY` (screen).

## 8. Bullet / list items
Bullets use the SAME weight as body copy: Poppins Regular, slate `#2B3D4F`,
10–11pt. They are NEVER bold or emphasised. Only component titles (callout
panel title, card title, table header) may be bold; the content beneath them
— including any list items — stays normal weight.

PDF: `bs.bullet_list(c, x, y, items, w)` (module primitive).
DOCX: `bullets(doc, items)` helper (uses List Bullet style, force bold=False).
PPTX: `bullet_list(slide, x, y, w, items)` helper.

## 8. Voice
Confident, outcome-led, plain. Lead with the result. Echo the deck:
"Delivering amazing…", "We helped … scale 5X." Avoid hype beyond brand vocab.
