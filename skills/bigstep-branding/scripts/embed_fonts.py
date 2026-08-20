"""
Embed TrueType fonts into a .docx so the brand typeface (Poppins) renders in
Microsoft Word even on machines where the font is NOT installed.

Word embeds fonts as ECMA-376 "obfuscated" binaries (.odttf): the first 32
bytes of the TTF are XORed with the embedding GUID (bytes in reverse order).
This module post-processes a saved .docx:

    from embed_fonts import embed_fonts_in_docx
    embed_fonts_in_docx("out.docx", [{
        "name": "Poppins",
        "regular": ".../Poppins-Regular.ttf",
        "bold":    ".../Poppins-Bold.ttf",
    }])

Only the styles you supply are embedded; supply at least regular + bold (this
brand uses bold for weight). italic / bolditalic are optional keys.
"""
import io
import os
import uuid
import zipfile
from lxml import etree

W  = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R  = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
FONT_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/font"
NS = {"w": W, "r": R}


def _obfuscate(ttf_bytes, guid_hex):
    """XOR first 32 bytes with the 16 GUID bytes in reverse, cycled."""
    key = bytes.fromhex(guid_hex)              # 16 bytes
    data = bytearray(ttf_bytes)
    for i in range(32):
        data[i] ^= key[15 - (i % 16)]
    return bytes(data)


def embed_fonts_in_docx(path, fonts):
    zin = zipfile.ZipFile(path, "r")
    parts = {n: zin.read(n) for n in zin.namelist()}
    zin.close()

    # ---- fontTable.xml : add <w:font><w:embed.../></w:font> ----
    ft = etree.fromstring(parts["word/fontTable.xml"])
    rels_root = etree.Element(f"{{{PR}}}Relationships")
    if "word/_rels/fontTable.xml.rels" in parts:
        rels_root = etree.fromstring(parts["word/_rels/fontTable.xml.rels"])

    style_tag = {"regular": "embedRegular", "bold": "embedBold",
                 "italic": "embedItalic", "bolditalic": "embedBoldItalic"}
    fidx = 1
    ridx = 1000
    for font in fonts:
        name = font["name"]
        # find or create the <w:font w:name="..."> element
        fel = None
        for f in ft.findall(f"{{{W}}}font"):
            if f.get(f"{{{W}}}name") == name:
                fel = f
                break
        if fel is None:
            fel = etree.SubElement(ft, f"{{{W}}}font")
            fel.set(f"{{{W}}}name", name)
        for style, ttf in font.items():
            if style == "name" or not ttf or not os.path.exists(ttf):
                continue
            guid = uuid.uuid4().hex.upper()                 # 32 hex chars
            part_name = f"word/fonts/font{fidx}.odttf"
            with open(ttf, "rb") as fh:
                parts[part_name] = _obfuscate(fh.read(), guid)
            rid = f"rIdFont{ridx}"
            emb = etree.SubElement(fel, f"{{{W}}}{style_tag[style]}")
            emb.set(f"{{{R}}}id", rid)
            emb.set(f"{{{W}}}fontKey", "{" + "-".join(
                [guid[0:8], guid[8:12], guid[12:16], guid[16:20], guid[20:32]]) + "}")
            emb.set(f"{{{W}}}subsetted", "false")
            rel = etree.SubElement(rels_root, f"{{{PR}}}Relationship")
            rel.set("Id", rid); rel.set("Type", FONT_REL)
            rel.set("Target", f"fonts/font{fidx}.odttf")
            fidx += 1
            ridx += 1
    parts["word/fontTable.xml"] = etree.tostring(ft, xml_declaration=True,
                                                 encoding="UTF-8", standalone=True)
    parts["word/_rels/fontTable.xml.rels"] = etree.tostring(
        rels_root, xml_declaration=True, encoding="UTF-8", standalone=True)

    # ---- [Content_Types].xml : Default odttf ----
    ctx = etree.fromstring(parts["[Content_Types].xml"])
    if not any(d.get("Extension") == "odttf" for d in ctx.findall(f"{{{CT}}}Default")):
        d = etree.SubElement(ctx, f"{{{CT}}}Default")
        d.set("Extension", "odttf")
        d.set("ContentType", "application/vnd.openxmlformats-officedocument.obfuscatedFont")
    parts["[Content_Types].xml"] = etree.tostring(ctx, xml_declaration=True,
                                                  encoding="UTF-8", standalone=True)

    # ---- settings.xml : turn embedding on ----
    st = etree.fromstring(parts["word/settings.xml"])
    if st.find(f"{{{W}}}embedTrueTypeFonts") is None:
        st.insert(0, etree.Element(f"{{{W}}}embedTrueTypeFonts"))
    if st.find(f"{{{W}}}saveSubsetFonts") is None:
        st.insert(1, etree.Element(f"{{{W}}}saveSubsetFonts"))
    parts["word/settings.xml"] = etree.tostring(st, xml_declaration=True,
                                                encoding="UTF-8", standalone=True)

    # ---- rewrite the package ----
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, data in parts.items():
            zout.writestr(n, data)
    with open(path, "wb") as fh:
        fh.write(buf.getvalue())
    return path
