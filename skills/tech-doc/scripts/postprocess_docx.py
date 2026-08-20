"""Post-process a pandoc-generated DOCX so every table spans the full text width
(page width minus margins) instead of pandoc's content-based auto width.

Usage: python postprocess_docx.py <file.docx>
"""
import re
import shutil
import sys
import zipfile

TARGET_DXA = 9360  # ~6.5in text area (Letter, 1in margins) in twips


def main(path: str) -> None:
    zin = zipfile.ZipFile(path)
    items = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    xml = items["word/document.xml"].decode("utf-8")

    # 1. Every table → 100% width + autofit layout.
    xml = re.sub(
        r"<w:tblW\b[^>]*/>",
        '<w:tblW w:type="pct" w:w="5000"/><w:tblLayout w:type="autofit"/>',
        xml,
    )

    # 2. Rescale each <w:tblGrid> so columns sum to the full text width,
    #    preserving pandoc's relative column proportions.
    def fix_grid(m: "re.Match[str]") -> str:
        block = m.group(0)
        widths = [int(w) for w in re.findall(r'<w:gridCol\b[^>]*w:w="(\d+)"', block)]
        if not widths:
            return block
        total = sum(widths) or len(widths)
        scaled = [max(1, round(w * TARGET_DXA / total)) for w in widths]
        cols = "".join(f'<w:gridCol w:w="{w}"/>' for w in scaled)
        return f"<w:tblGrid>{cols}</w:tblGrid>"

    xml = re.sub(r"<w:tblGrid>.*?</w:tblGrid>", fix_grid, xml, flags=re.S)

    # 2b. Cell padding — give every table breathing room inside its cells.
    #     tblCellMar must sit just before tblLook in tblPr (schema order).
    cell_mar = (
        "<w:tblCellMar>"
        '<w:top w:w="80" w:type="dxa"/>'
        '<w:left w:w="120" w:type="dxa"/>'
        '<w:bottom w:w="80" w:type="dxa"/>'
        '<w:right w:w="120" w:type="dxa"/>'
        "</w:tblCellMar>"
    )
    if "<w:tblCellMar>" not in xml:
        xml = xml.replace("<w:tblLook", cell_mar + "<w:tblLook")

    # 2c. Keep each table row intact (no mid-row split across a page break).
    xml = re.sub(r"<w:trPr>(?!<w:cantSplit)", "<w:trPr><w:cantSplit/>", xml)
    xml = re.sub(r"<w:tr>(?!<w:trPr>)", "<w:tr><w:trPr><w:cantSplit/></w:trPr>", xml)

    # 3. Per-paragraph polish:
    #    - every top-level section (Heading1) starts on a new page
    #    - figure images and their "Figure N — …" captions are centred
    state = {"seen_h1": False}  # cover (before the first section) is left untouched
    h1_re = re.compile(r'<w:pStyle w:val="Heading1"\s*/>')

    def polish_para(m: "re.Match[str]") -> str:
        p = m.group(0)
        is_h1 = h1_re.search(p) is not None
        text = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p))
        is_cap = text.strip().startswith("Figure ")
        # only centre images once we're past the cover (inside the body)
        is_img = "<w:drawing" in p and state["seen_h1"]
        if is_h1:
            state["seen_h1"] = True
        if not (is_img or is_cap or is_h1):
            return p
        # Assemble the extra paragraph properties to inject:
        #  - centre images and captions
        #  - keep an image with the caption that follows it
        #  - add a little space around the figure block
        extras = ""
        if (is_img or is_cap) and "<w:jc " not in p:
            extras += '<w:jc w:val="center"/>'
        if is_img:
            if "<w:keepNext" not in p:
                extras += "<w:keepNext/>"
            if "<w:spacing " not in p:
                extras += '<w:spacing w:before="160" w:after="40"/>'
        if is_cap and "<w:spacing " not in p:
            extras += '<w:spacing w:before="40" w:after="200"/>'
        if "<w:pPr>" in p:
            if extras:
                p = p.replace("<w:pPr>", "<w:pPr>" + extras, 1)
            if is_h1 and "<w:pageBreakBefore" not in p:
                p = h1_re.sub(
                    lambda mm: mm.group(0) + "<w:pageBreakBefore/>", p, count=1
                )
        else:
            p = re.sub(
                r"(<w:p\b[^>]*>)", r"\1" + "<w:pPr>" + extras + "</w:pPr>", p, count=1
            )
        return p

    xml = re.sub(r"<w:p\b[^>]*>.*?</w:p>", polish_para, xml, flags=re.S)

    items["word/document.xml"] = xml.encode("utf-8")

    tmp = path + ".tmp"
    zo = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    for name, data in items.items():
        zo.writestr(name, data)
    zo.close()
    shutil.move(tmp, path)
    print(
        "Tables full-width + padded; rows kept intact; sections page-broken; "
        "figures centred & kept with captions:",
        path,
    )


if __name__ == "__main__":
    main(sys.argv[1])
