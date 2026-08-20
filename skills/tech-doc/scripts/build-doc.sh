#!/usr/bin/env bash
# Build a BigStep-branded technical document: markdown -> DOCX -> PDF.
#
#   build-doc.sh docs/Acme-Technical-Documentation.md --client "Acme"
#
# Options:
#   --client NAME     name in the footer confidentiality line (default: none)
#   --reference FILE  Word template to style from (default: the skill's)
#   --diagrams DIR    render every *.dot in DIR to PNG with graphviz first
#   --no-pdf          stop after the DOCX
#
# Requires pandoc; PDF also needs LibreOffice (`soffice`).
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REF="$SKILL_DIR/assets/bigstep-reference.docx"
CLIENT=""
DIAGRAMS=""
MAKE_PDF=1
MD=""

while [ $# -gt 0 ]; do
  case "$1" in
    --client)    CLIENT="$2"; shift 2 ;;
    --reference) REF="$2"; shift 2 ;;
    --diagrams)  DIAGRAMS="$2"; shift 2 ;;
    --no-pdf)    MAKE_PDF=0; shift ;;
    -h|--help)   sed -n '2,12p' "${BASH_SOURCE[0]}" | sed 's/^# \?//'; exit 0 ;;
    *)           MD="$1"; shift ;;
  esac
done

[ -n "$MD" ] || { echo "usage: build-doc.sh <markdown> [--client NAME] [--diagrams DIR] [--no-pdf]" >&2; exit 2; }
[ -f "$MD" ] || { echo "no such file: $MD" >&2; exit 2; }
command -v pandoc >/dev/null || { echo "pandoc not found — brew install pandoc" >&2; exit 127; }

DIR="$(cd "$(dirname "$MD")" && pwd)"
BASE="$(basename "$MD" .md)"
DOCX="$DIR/$BASE.docx"
PDF="$DIR/$BASE.pdf"

# 1. diagrams — .dot sources are the checked-in truth, PNGs are derived
if [ -n "$DIAGRAMS" ]; then
  command -v dot >/dev/null || { echo "graphviz not found — brew install graphviz" >&2; exit 127; }
  for src in "$DIAGRAMS"/*.dot; do
    [ -e "$src" ] || break
    dot -Tpng -Gdpi=150 "$src" -o "${src%.dot}.png"
    echo "diagram: ${src%.dot}.png"
  done
fi

# 2. stamp the client name into a scratch copy of the template
REF_USED="$REF"
if [ -n "$CLIENT" ]; then
  REF_USED="$(mktemp -t reference).docx"
  python3 "$SKILL_DIR/scripts/make_reference_docx.py" "$REF" "$REF_USED" \
    --replace "{{CLIENT}}=>$CLIENT" >/dev/null
fi

# 3. markdown -> DOCX, styled by the reference doc
pandoc "$MD" \
  --reference-doc="$REF_USED" \
  --from=gfm+tex_math_dollars+raw_attribute+fenced_divs+attributes \
  --resource-path="$DIR" \
  -o "$DOCX"

# 4. fix what pandoc can't express: full-width tables, page break per section,
#    centred figures kept with their captions
python3 "$SKILL_DIR/scripts/postprocess_docx.py" "$DOCX"

[ "$REF_USED" = "$REF" ] || rm -f "$REF_USED"
echo "Built: $DOCX"

# 5. DOCX -> PDF
if [ "$MAKE_PDF" = 1 ]; then
  SOFFICE="${SOFFICE:-$(command -v soffice || echo /Applications/LibreOffice.app/Contents/MacOS/soffice)}"
  if [ ! -x "$SOFFICE" ]; then
    echo "LibreOffice not found — skipping PDF (brew install --cask libreoffice)" >&2
    exit 0
  fi
  rm -f "$PDF"
  "$SOFFICE" --headless -env:UserInstallation=file:///tmp/lo-builddoc \
    --convert-to pdf --outdir "$DIR" "$DOCX" >/dev/null 2>&1
  echo "Built: $PDF"
fi
