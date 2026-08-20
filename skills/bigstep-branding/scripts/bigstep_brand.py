"""
BigStep Technologies — brand design system (v2).

This is the single source of truth for BigStep-branded deliverables. It ships:
  * exact palette (sampled from the official Corporate Profile)
  * the exact brand typeface (Poppins — the font embedded in the deck/site)
  * logo assets + a ReportLab-safe logo loader
  * the design language as reusable ReportLab primitives:
        - concentric-ring background motif (the brand's signature texture)
        - cover / section-divider page builders
        - content-page header & footer bands
        - stat cards, callout panels, label chips, branded tables

Usage (PDF):
    import sys; sys.path.insert(0, "<skill>/scripts")
    import bigstep_brand as bs
    bs.register_fonts()
    ...compose pages with bs.cover_page(c, ...), bs.page_frame(c, ...), etc.

For docx / pptx, use the palette + FONT names below and install the bundled
Poppins TTFs (assets/fonts). See the references/ recipes.
"""

import os
from pathlib import Path

# --------------------------------------------------------------------------- #
# PALETTE  (exact hex sampled from the Corporate Profile)
# --------------------------------------------------------------------------- #
class C:
    PRIMARY  = "#1C62EC"   # BigStep blue — primary
    PRIMARY_D = "#0F3FA6"  # darker blue for depth/gradients
    CYAN     = "#3FC7F2"   # logo accent cyan — accents only
    NAVY     = "#041342"   # deep navy — display/heading text
    SLATE    = "#2B3D4F"   # body text on light
    TINT     = "#E4F2FF"   # light-blue panel fill
    TINT2    = "#D4E6FF"   # deeper light-BLUE tint — zebra rows / alt panels (no purple)
    RING     = "#EAF1FE"   # faint ring motif on white
    RING_ON_BLUE = "#3E7BEF"  # ring motif on blue bg
    GOLD     = "#FDCA0E"   # rare highlight only
    WHITE    = "#FFFFFF"
    PAGE     = "#FFFFFF"
    MUTED    = "#6B7A8D"   # captions / footer


def hx(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def rl(h):
    from reportlab.lib.colors import Color
    r, g, b = hx(h)
    return Color(r/255, g/255, b/255)


# --------------------------------------------------------------------------- #
# TYPOGRAPHY  — Poppins is the BigStep brand face (embedded in the deck & site)
# --------------------------------------------------------------------------- #
class FONT:
    # ReportLab registered names (set by register_fonts())
    LIGHT   = "Poppins-Light"
    REGULAR = "Poppins"
    MEDIUM  = "Poppins-Medium"
    SEMI    = "Poppins-SemiBold"
    BOLD    = "Poppins-Bold"
    XBOLD   = "Poppins-ExtraBold"
    # Office (docx/pptx) family name — install the bundled TTFs
    OFFICE  = "Poppins"
    OFFICE_FALLBACK = "Calibri"


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
FONTS = ASSETS / "fonts"

_FONTS_REGISTERED = False


def register_fonts():
    """Register the bundled Poppins TTFs with ReportLab. Idempotent."""
    global _FONTS_REGISTERED
    if _FONTS_REGISTERED:
        return
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    mapping = {
        FONT.LIGHT:   "Poppins-Light.ttf",
        FONT.REGULAR: "Poppins-Regular.ttf",
        FONT.MEDIUM:  "Poppins-Medium.ttf",
        FONT.SEMI:    "Poppins-SemiBold.ttf",
        FONT.BOLD:    "Poppins-Bold.ttf",
        FONT.XBOLD:   "Poppins-ExtraBold.ttf",
    }
    for name, fn in mapping.items():
        path = FONTS / fn
        if path.exists():
            pdfmetrics.registerFont(TTFont(name, str(path)))
    _FONTS_REGISTERED = True


# --------------------------------------------------------------------------- #
# LOGO
# --------------------------------------------------------------------------- #
def logo_path(variant="color"):
    return str(ASSETS / {
        "color": "bigstep_logo_color.png",
        "white": "bigstep_logo_white.png",
        "mark":  "bigstep_mark.png",
    }[variant])


def _read_aspect(variant):
    """height/width of a logo asset, read from the PNG so it never drifts if an
    asset is re-exported at a different size."""
    from PIL import Image as _PILImage
    w, h = _PILImage.open(logo_path(variant)).size
    return h / w


_ASPECT = {v: _read_aspect(v) for v in ("color", "white", "mark")}


def reportlab_logo(variant="color", matte=C.WHITE):
    """ReportLab renders alpha PNGs unreliably; flatten onto `matte` and return
    an opaque ImageReader that always draws (mask=None)."""
    from PIL import Image
    from reportlab.lib.utils import ImageReader
    img = Image.open(logo_path(variant)).convert("RGBA")
    bg = Image.new("RGBA", img.size, (*hx(matte), 255))
    return ImageReader(Image.alpha_composite(bg, img).convert("RGB"))


def draw_logo(c, variant, x, y, width, matte=None, anchor="sw"):
    """Draw a logo with EXPLICIT width+height (always pass both — passing only
    width with preserveAspectRatio mis-positions the image in ReportLab)."""
    if matte is None:
        matte = C.PRIMARY if variant == "white" else C.WHITE
    h = width * _ASPECT[variant]
    c.drawImage(reportlab_logo(variant, matte), x, y, width=width, height=h,
                mask=None, anchor=anchor)
    return h


# --------------------------------------------------------------------------- #
# BRAND FACTS
# --------------------------------------------------------------------------- #
BRAND = {
    "company": "BigStep Technologies",
    "website": "www.bigsteptech.com",
    "email": "info@bigsteptech.com",
    "tagline": "Delivering amazing Software, AI & Digital Experiences to Enterprises & Startups Globally",
    "founded": 2008,
    "hq": "Gurugram (New Delhi NCR, India)",
    "descriptor": "AI-First, Cloud-Native Custom Software Engineering, Product Development & Data/AI Services",
}


# ============================ DESIGN PRIMITIVES (ReportLab) ================= #
# All take a reportlab canvas `c`. Page size assumed A4 landscape OR portrait;
# pass page width/height (pw, ph) in points.

from reportlab.lib.units import mm  # noqa: E402


def concentric(c, cx, cy, color, n=7, r0=14*mm, step=12*mm, lw=1.1, alpha=1.0):
    """Signature faint concentric-ring motif. Draw clipped near a corner."""
    c.saveState()
    c.setLineWidth(lw)
    col = rl(color)
    try:
        col.alpha = alpha
    except Exception:
        pass
    c.setStrokeColor(col)
    for i in range(n):
        c.circle(cx, cy, r0 + i*step, stroke=1, fill=0)
    c.restoreState()


def _clip_rect(c, x, y, w, h):
    p = c.beginPath(); p.rect(x, y, w, h); c.clipPath(p, stroke=0, fill=0)


def cover_page(c, pw, ph, title, subtitle=None, kicker=None, footer_chips=None):
    """Full-bleed blue cover with rings, white logo, two-tone(white) title."""
    c.saveState()
    c.setFillColor(rl(C.PRIMARY)); c.rect(0, 0, pw, ph, fill=1, stroke=0)
    # subtle darker wash bottom
    # rings top-right and bottom-left, clipped to corners
    c.saveState(); _clip_rect(c, pw-70*mm, ph-70*mm, 70*mm, 70*mm)
    concentric(c, pw-6*mm, ph-6*mm, C.RING_ON_BLUE, n=9, r0=8*mm, step=9*mm, lw=1.0)
    c.restoreState()
    c.saveState(); _clip_rect(c, 0, 0, 60*mm, 60*mm)
    concentric(c, 2*mm, 2*mm, C.RING_ON_BLUE, n=8, r0=8*mm, step=9*mm, lw=1.0)
    c.restoreState()
    # logo
    draw_logo(c, "white", 18*mm, ph-30*mm, 44*mm)
    # cyan accent bar
    c.setFillColor(rl(C.CYAN)); c.rect(18*mm, ph*0.56, 26*mm, 2.6*mm, fill=1, stroke=0)
    if kicker:
        c.setFont(FONT.SEMI, 12); c.setFillColor(rl(C.CYAN))
        c.drawString(18*mm, ph*0.56+7*mm, kicker.upper())
    # title (wrapped, white, big)
    c.setFillColor(rl(C.WHITE))
    _draw_wrapped(c, title, 18*mm, ph*0.50, pw-90*mm, FONT.XBOLD, 34, 40, color=C.WHITE)
    if subtitle:
        c.setFillColor(rl("#D9E6FF"))
        _draw_wrapped(c, subtitle, 18*mm, ph*0.30, pw-70*mm, FONT.REGULAR, 13, 19, color="#D9E6FF")
    # bottom chip bar (service-bar look)
    if footer_chips:
        bar_h = 12*mm
        c.setFillColor(rl(C.PRIMARY_D)); c.rect(0, 0, pw, bar_h, fill=1, stroke=0)
        c.setFont(FONT.MEDIUM, 9.5); c.setFillColor(rl(C.WHITE))
        txt = "      |      ".join(footer_chips)
        c.drawCentredString(pw/2, bar_h/2-3, txt)
    c.restoreState()


def section_divider(c, pw, ph, number, title):
    """Blue section break: big faint number, white title, accent."""
    c.saveState()
    c.setFillColor(rl(C.PRIMARY)); c.rect(0, 0, pw, ph, fill=1, stroke=0)
    c.saveState(); _clip_rect(c, pw-80*mm, 0, 80*mm, 80*mm)
    concentric(c, pw-4*mm, 4*mm, C.RING_ON_BLUE, n=9, r0=8*mm, step=10*mm)
    c.restoreState()
    draw_logo(c, "white", 18*mm, ph-26*mm, 36*mm)
    # huge ghost number
    c.setFillColor(rl(C.PRIMARY_D)); c.setFont(FONT.XBOLD, 150)
    c.drawString(14*mm, ph*0.34, str(number))
    c.setFillColor(rl(C.CYAN)); c.rect(20*mm, ph*0.60, 24*mm, 2.6*mm, fill=1, stroke=0)
    c.setFillColor(rl(C.WHITE))
    _draw_wrapped(c, title, 20*mm, ph*0.55, pw-60*mm, FONT.BOLD, 30, 36, color=C.WHITE)
    _footer(c, pw, on_dark=True)
    c.restoreState()


def closing_page(c, pw, ph, title, subtitle=None, contact=None, title_size=38):
    """Blue hero / closing page. The cyan accent sits ABOVE the whole title
    block with a clear gap — never between lines — so it can't overlap text.

    title: a string (auto-wrapped) OR a list of explicit lines.
    contact: optional dict {title, lines:[...], meta} -> white contact card.
    """
    c.saveState()
    c.setFillColor(rl(C.PRIMARY)); c.rect(0, 0, pw, ph, fill=1, stroke=0)
    c.saveState(); _clip_rect(c, pw-90*mm, ph-90*mm, 90*mm, 90*mm)
    concentric(c, pw-4*mm, ph-4*mm, C.RING_ON_BLUE, n=10, r0=8*mm, step=10*mm)
    c.restoreState()
    c.saveState(); _clip_rect(c, 0, 0, 70*mm, 70*mm)
    concentric(c, 2*mm, 2*mm, C.RING_ON_BLUE, n=8, r0=8*mm, step=10*mm)
    c.restoreState()
    draw_logo(c, "white", 18*mm, ph-34*mm, 48*mm)

    lines = title if isinstance(title, (list, tuple)) else _wrap(title, FONT.XBOLD, title_size, pw-60*mm)
    leading = title_size * 1.16                       # pt
    first_baseline = ph * 0.52
    cap = title_size * 0.72                            # approx cap height (pt)
    # accent ABOVE the first line, with a 6mm gap above the cap height
    accent_y = first_baseline + cap + 6*mm
    c.setFillColor(rl(C.CYAN)); c.rect(18*mm, accent_y, 24*mm, 2.6*mm, fill=1, stroke=0)
    c.setFillColor(rl(C.WHITE)); c.setFont(FONT.XBOLD, title_size)
    y = first_baseline
    for ln in lines:
        c.drawString(18*mm, y, ln); y -= leading
    if subtitle:
        _draw_wrapped(c, subtitle, 18*mm, y - 2*mm, pw-70*mm, FONT.REGULAR, 13, 19, color="#D9E6FF")
    if contact:
        cw = pw - 36*mm; ch = 34*mm; cx = 18*mm; cy = 38*mm
        c.setFillColor(rl(C.WHITE)); c.roundRect(cx, cy, cw, ch, 4*mm, fill=1, stroke=0)
        c.setFillColor(rl(C.CYAN)); c.rect(cx, cy, 2.6*mm, ch, fill=1, stroke=0)
        c.setFillColor(rl(C.NAVY)); c.setFont(FONT.SEMI, 13)
        c.drawString(cx+8*mm, cy+ch-11*mm, contact.get("title", "Contact Us"))
        c.setFillColor(rl(C.SLATE)); c.setFont(FONT.REGULAR, 11)
        yy = cy+ch-19*mm
        for line in contact.get("lines", []):
            c.drawString(cx+8*mm, yy, line); yy -= 6*mm
        if contact.get("meta"):
            c.setFont(FONT.REGULAR, 9); c.setFillColor(rl(C.MUTED))
            c.drawRightString(cx+cw-8*mm, cy+8*mm, contact["meta"])
    _footer(c, pw, on_dark=True)
    c.restoreState()


def page_frame(c, pw, ph, page_no=None, header_label=None):
    """Header (small logo top-left) and footer for a white content page.
    No line below the logo — the accent line goes under the page heading
    (drawn by the caller via two_tone or manually)."""
    c.saveState()
    c.setFillColor(rl(C.WHITE)); c.rect(0, 0, pw, ph, fill=1, stroke=0)
    c.saveState(); _clip_rect(c, pw-55*mm, ph-55*mm, 55*mm, 55*mm)
    concentric(c, pw-2*mm, ph-2*mm, C.RING, n=7, r0=8*mm, step=9*mm, lw=1.0)
    c.restoreState()
    # small logo, high
    draw_logo(c, "color", 18*mm, ph-14*mm, 16*mm)
    if header_label:
        c.setFont(FONT.MEDIUM, 8.5); c.setFillColor(rl(C.MUTED))
        c.drawRightString(pw-18*mm, ph-11*mm, header_label.upper())
    _footer(c, pw, page_no=page_no)
    c.restoreState()


def _footer(c, pw, page_no=None, on_dark=False):
    y = 13*mm                       # baseline, raised for a clear bottom margin
    col = C.WHITE if on_dark else C.MUTED
    size = 8
    # mark sized to the text and vertically CENTERED on the text line so it is
    # never oversized or clipped; height kept modest with a clear page margin.
    mark_h = 3.6*mm
    mark_w = mark_h / _ASPECT["mark"]
    text_center = y + (size * 0.72 / 2) * (25.4/72)   # ~ text vertical centre
    mark_y = text_center - mark_h/2                    # sw anchor (bottom)
    draw_logo(c, "mark", 18*mm, mark_y, mark_w,
              matte=(C.PRIMARY if on_dark else C.WHITE))
    c.setFont(FONT.MEDIUM, size); c.setFillColor(rl(col))
    c.drawString(18*mm + mark_w + 2.2*mm, y, BRAND["website"])
    if page_no is not None:
        c.drawRightString(pw-18*mm, y, f"{page_no:02d}")


# ----- text helpers -----
def _wrap(text, font, size, max_w):
    from reportlab.pdfbase.pdfmetrics import stringWidth
    words = text.split(); lines = []; cur = ""
    for w in words:
        t = (cur + " " + w).strip()
        if stringWidth(t, font, size) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def _draw_wrapped(c, text, x, y, max_w, font, size, leading, color=None):
    if color:
        c.setFillColor(rl(color))
    c.setFont(font, size)
    yy = y
    for ln in _wrap(text, font, size, max_w):
        c.drawString(x, yy, ln); yy -= leading
    return yy


# ----- content components -----
def chip(c, x, y, text, fill=None, fg=None):
    """Small rounded label chip (like the deck's 'About the Platform' labels)."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    fill = fill or C.TINT; fg = fg or C.NAVY
    pad = 4*mm; size = 10
    w = stringWidth(text, FONT.SEMI, size) + 2*pad
    h = 7.5*mm
    c.setFillColor(rl(fill)); c.roundRect(x, y, w, h, 2.2*mm, fill=1, stroke=0)
    c.setFillColor(rl(fg)); c.setFont(FONT.SEMI, size)
    c.drawString(x+pad, y+h/2-3.4, text)
    return w, h


def two_tone(c, x, y, lead, tail, size=20, on_dark=False):
    """lead (navy/white) + tail (blue/white) heading with cyan underline."""
    from reportlab.pdfbase.pdfmetrics import stringWidth
    c.setFont(FONT.BOLD, size)
    c.setFillColor(rl(C.WHITE if on_dark else C.NAVY)); c.drawString(x, y, lead)
    lw = stringWidth(lead, FONT.BOLD, size)
    c.setFillColor(rl(C.WHITE if on_dark else C.PRIMARY)); c.drawString(x+lw, y, tail)
    c.setFillColor(rl(C.CYAN)); c.rect(x, y-3.5*mm, 16*mm, 1.8*mm, fill=1, stroke=0)


def stat_card(c, x, y, w, h, value, label, accent=None):
    accent = accent or C.PRIMARY
    c.setFillColor(rl(C.TINT)); c.roundRect(x, y, w, h, 3*mm, fill=1, stroke=0)
    c.setFillColor(rl(accent)); c.rect(x, y, 2.2*mm, h, fill=1, stroke=0)
    c.setFillColor(rl(C.NAVY)); c.setFont(FONT.XBOLD, 22)
    c.drawString(x+7*mm, y+h-13*mm, value)
    c.setFillColor(rl(C.SLATE)); c.setFont(FONT.MEDIUM, 8.6)
    for i, ln in enumerate(_wrap(label, FONT.MEDIUM, 8.6, w-10*mm)):
        c.drawString(x+7*mm, y+h-19*mm-i*4.4*mm, ln)


def callout(c, x, y, w, title, lines, fill=None, accent=None, pad=6*mm):
    """Rounded tinted panel with a colored left rule. Returns its height."""
    fill = fill or C.TINT; accent = accent or C.PRIMARY
    body_lines = []
    for ln in lines:
        body_lines.extend(_wrap(ln, FONT.REGULAR, 9.5, w-2*pad) or [""])
        body_lines.append(None)  # paragraph gap marker
    h = pad + 6*mm + len(body_lines)*4.8*mm + pad - 2*mm
    c.setFillColor(rl(fill)); c.roundRect(x, y-h, w, h, 3*mm, fill=1, stroke=0)
    c.setFillColor(rl(accent)); c.rect(x, y-h, 2.4*mm, h, fill=1, stroke=0)
    c.setFillColor(rl(C.NAVY)); c.setFont(FONT.SEMI, 11)
    c.drawString(x+pad, y-pad-2*mm, title)
    c.setFont(FONT.REGULAR, 9.5); c.setFillColor(rl(C.SLATE))
    yy = y-pad-9*mm
    for ln in body_lines:
        if ln is None:
            yy -= 1.6*mm; continue
        c.drawString(x+pad, yy, ln); yy -= 4.8*mm
    return h


def bullet_list(c, x, y, items, w, size=9.5, leading=14, color=None, bullet="•"):
    """Normal-weight body-text bullet list. Items are Poppins Regular, slate,
    and are NEVER bold — bullets match the body paragraph style exactly.
    Returns the y position after the last item."""
    color = color or C.SLATE
    c.setFont(FONT.REGULAR, size); c.setFillColor(rl(color))
    yy = y
    indent = 4*mm
    for item in items:
        lines = _wrap(item, FONT.REGULAR, size, w - indent)
        c.drawString(x, yy, bullet)
        for i, ln in enumerate(lines):
            c.drawString(x + indent, yy, ln)
            yy -= leading
        yy -= 2                           # paragraph gap between items
    return yy


def branded_table_style(header_fill=None):
    """Return a reportlab TableStyle for a branded table."""
    from reportlab.platypus import TableStyle
    hf = header_fill or C.PRIMARY
    return TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl(hf)),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl(C.WHITE)),
        ("FONTNAME", (0, 0), (-1, 0), FONT.SEMI),
        ("FONTSIZE", (0, 0), (-1, 0), 9.5),
        ("FONTNAME", (0, 1), (-1, -1), FONT.REGULAR),
        ("FONTSIZE", (0, 1), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 1), (-1, -1), rl(C.SLATE)),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [rl(C.WHITE), rl(C.TINT2)]),
        ("LINEBELOW", (0, 0), (-1, 0), 0, rl(C.WHITE)),
        ("GRID", (0, 0), (-1, -1), 0.5, rl(C.TINT)),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
    ])
