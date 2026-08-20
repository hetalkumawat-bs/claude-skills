#!/usr/bin/env python3
"""Turn a branded Word document into a clean pandoc `--reference-doc` template.

A .docx you were handed — a proposal, an SoW, last quarter's report — carries
that whole document inside `word/document.xml`. Pandoc reads only the styles,
theme, numbering, headers and footers from a reference doc, so the body is dead
weight: it makes the template ten times larger and ships the previous client's
text to whoever gets your repo.

This strips the body to a single empty paragraph, keeps the section properties
(page size, margins, header/footer references), drops media and customXml parts
nothing references any more, and optionally rewrites literal strings in the
headers and footers — the client name in a confidentiality line, typically.

Usage:
    make_reference_docx.py IN.docx OUT.docx [--replace "old text=>new text" ...]

Example:
    make_reference_docx.py proposal.docx reference.docx \\
        --replace "Acme Corp=>{{CLIENT}}"
"""

from __future__ import annotations

import re
import shutil
import sys
import zipfile

USAGE = __doc__.split("Usage:")[1].strip()


def parse_args(argv: list[str]) -> tuple[str, str, list[tuple[str, str]]]:
    positional: list[str] = []
    replacements: list[tuple[str, str]] = []
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg == "--replace":
            i += 1
            if i >= len(argv) or "=>" not in argv[i]:
                sys.exit('--replace expects "old text=>new text"')
            old, new = argv[i].split("=>", 1)
            replacements.append((old, new))
        elif arg in ("-h", "--help"):
            sys.exit(USAGE)
        else:
            positional.append(arg)
        i += 1
    if len(positional) != 2:
        sys.exit(USAGE)
    return positional[0], positional[1], replacements


def strip_body(document_xml: str) -> str:
    """Keep the document element and its final sectPr; drop everything else."""
    start = document_xml.find("<w:body>")
    if start < 0:
        sys.exit("no <w:body> in word/document.xml — is this a .docx?")
    head = document_xml[: start + len("<w:body>")]

    sect = ""
    sect_start = document_xml.rfind("<w:sectPr")
    if sect_start >= 0:
        sect_end = document_xml.find("</w:sectPr>", sect_start)
        sect = (
            document_xml[sect_start : sect_end + len("</w:sectPr>")]
            if sect_end >= 0
            else document_xml[sect_start : document_xml.find(">", sect_start) + 1]
        )
    return head + "<w:p/>" + sect + "</w:body></w:document>"


def referenced_media(items: dict[str, bytes]) -> set[str]:
    """Media still reachable from a header or footer part."""
    keep: set[str] = set()
    for name, data in items.items():
        if not name.startswith("word/_rels/"):
            continue
        if name == "word/_rels/document.xml.rels":
            continue  # the body is gone, so its media are unreachable
        for target in re.findall(rb'Target="([^"]+)"', data):
            t = target.decode("utf-8")
            if t.startswith("media/"):
                keep.add("word/" + t)
    return keep


def prune_document_rels(rels_xml: str) -> str:
    """Drop image, hyperlink and customXml relationships the empty body can't use."""

    def keep(rel: str) -> bool:
        target = re.search(r'Target="([^"]+)"', rel)
        rtype = re.search(r'Type="[^"]*/(\w+)"', rel)
        if target and ("customXml" in target.group(1) or target.group(1).startswith("media/")):
            return False
        return not (rtype and rtype.group(1) in {"image", "hyperlink", "customXml"})

    return re.sub(r"<Relationship\b[^>]*/>", lambda m: m.group(0) if keep(m.group(0)) else "", rels_xml)


def main() -> None:
    src, dst, replacements = parse_args(sys.argv[1:])

    with zipfile.ZipFile(src) as zin:
        items = {n: zin.read(n) for n in zin.namelist() if not n.endswith("/")}

    before = sum(len(v) for v in items.values())

    if "word/document.xml" not in items:
        sys.exit(f"{src} has no word/document.xml — not a Word file")

    items["word/document.xml"] = strip_body(
        items["word/document.xml"].decode("utf-8")
    ).encode("utf-8")

    keep_media = referenced_media(items)
    dropped = [
        n
        for n in list(items)
        if (n.startswith("word/media/") and n not in keep_media) or n.startswith("customXml/")
    ]
    for name in dropped:
        del items[name]

    if "word/_rels/document.xml.rels" in items:
        items["word/_rels/document.xml.rels"] = prune_document_rels(
            items["word/_rels/document.xml.rels"].decode("utf-8")
        ).encode("utf-8")

    if "[Content_Types].xml" in items:
        ct = items["[Content_Types].xml"].decode("utf-8")
        ct = re.sub(r'<Override[^>]*PartName="/customXml/[^"]*"[^>]*/>', "", ct)
        items["[Content_Types].xml"] = ct.encode("utf-8")

    applied = {old: 0 for old, _ in replacements}
    for name in list(items):
        if not re.match(r"word/(header|footer)\d*\.xml$", name):
            continue
        xml = items[name].decode("utf-8")
        for old, new in replacements:
            if old in xml:
                applied[old] += xml.count(old)
                xml = xml.replace(old, new)
        items[name] = xml.encode("utf-8")

    # The body is empty, so any surviving <w:t> would be header/footer text only.
    leftover = re.findall(r"<w:t[^>]*>(.*?)</w:t>", items["word/document.xml"].decode("utf-8"))
    if leftover:
        sys.exit(f"body text survived the strip: {leftover[:3]}")

    tmp = dst + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, data in items.items():
            zout.writestr(name, data)
    shutil.move(tmp, dst)

    after = sum(len(v) for v in items.values())
    print(f"{src} -> {dst}")
    print(f"  body stripped, section properties kept ({before // 1024}KB -> {after // 1024}KB uncompressed)")
    if dropped:
        print(f"  dropped {len(dropped)} unreferenced part(s): {', '.join(sorted(dropped))}")
    for old, new in replacements:
        print(f'  header/footer: "{old}" -> "{new}" ({applied[old]}x)')
    if any(count == 0 for count in applied.values()):
        print("  WARNING: a --replace pattern matched nothing; check the exact wording")


if __name__ == "__main__":
    main()
