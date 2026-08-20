# Markdown conventions and the build

The document is written once, in markdown, and built to DOCX and PDF. Everything visual is
carried by the reference template plus one post-processing pass — there is no hand-editing of the
Word file, because the next build would throw it away.

```
document.md ──pandoc(--reference-doc)──▶ .docx ──postprocess──▶ .docx ──LibreOffice──▶ .pdf
```

## Markdown conventions the build depends on

**Cover** — pandoc fenced divs map to the template's Word styles:

```markdown
![Acme](assets/acme-logo.png){width=2.6in}

::: {custom-style="Title"}
Technical Documentation
:::

::: {custom-style="Subtitle"}
Acme — Platform Name
:::

&nbsp;

**Prepared for:** Acme Corporation

**Prepared by:** BigStep Technologies Pvt. Ltd. *(a Wondrlab Company)* · https://www.bigsteptech.com

![BigStep Technologies](assets/bigstep-logo.png){width=2.0in}

**Classification:** Confidential
```

`&nbsp;` on its own line is the only reliable vertical spacer — an empty line is collapsed.

**Section numbers are manual.** `# 1. Introduction`, `## 1.1 Purpose & Scope`. The template
carries no automatic numbering, so renumber by hand when you insert a section, and re-check the
TOC. Front-matter headings that must stay out of any generated TOC take
`{.unlisted .unnumbered}`.

**Every `#` starts a new page.** The post-processor puts a page break before every Heading 1, so
don't add `\newpage` and don't rely on `---` for separation.

**Figures** — image with an explicit width, then an italic caption paragraph on its own:

```markdown
![Acme high-level architecture](assets/architecture-highlevel.png){width=6.6in}

*Figure 1 — High-level layered architecture. Rendered from `assets/architecture-highlevel.dot`.*
```

`6.6in` is full text width in the template's Letter page with 0.75in margins; `4.3in` suits a
tall narrow diagram. The post-processor centres any paragraph starting with `Figure ` and keeps
the image on the same page as its caption, so the literal word **Figure** matters. Number
figures in one sequence across the whole document.

**Tables** are GFM pipe tables. The post-processor stretches every table to the full text width
and keeps rows from splitting across pages, so column widths in the markdown don't matter —
column *count* does: more than five columns is unreadable in portrait. Bold the load-bearing cell,
not the whole row.

**Code blocks** are fenced with a language tag. Keep them under ~15 lines; a long file listing
belongs in the repo, cited by path.

**Inline code** for every identifier: file paths, env var names, service names, hosts, table
names. It's the fastest signal that a name is literal and copy-pasteable.

## pandoc invocation

```bash
pandoc document.md \
  --reference-doc=reference.docx \
  --from=gfm+tex_math_dollars+raw_attribute+fenced_divs+attributes \
  --resource-path=. \
  -o document.docx
```

`fenced_divs` + `attributes` are what make the `custom-style` blocks and `{width=}` work;
`gfm` gives pipe tables and fenced code. `--resource-path` is the directory images resolve from.

## What the post-processor does

`scripts/postprocess_docx.py` edits `word/document.xml` for the things pandoc has no switch for:

1. Every table → 100% width, with its grid rescaled to preserve pandoc's column proportions.
2. Cell padding, so text doesn't touch the borders.
3. `cantSplit` on every row — no row broken across a page.
4. `pageBreakBefore` on every Heading 1.
5. Figure images and `Figure N` captions centred, with `keepNext` binding an image to its caption.

Idempotent: running it twice is harmless. It runs automatically inside `build-doc.sh`.

## The reference template

Pandoc reads only the styles, theme, numbering, headers and footers from `--reference-doc`. The
template's own body is ignored — which is exactly the trap:

> **A .docx you were handed still contains the whole document it came from.** The template this
> skill ships was derived from a client Scope of Work whose entire body text was still inside it,
> invisible to everyone, riding along into every export. Run any new template through
> `scripts/make_reference_docx.py` before committing it, and read the output: it prints every
> part it dropped.

```bash
python3 scripts/make_reference_docx.py branded.docx assets/reference.docx \
  --replace "Old Client Name=>{{CLIENT}}"
```

It strips the body to one empty paragraph, keeps the section properties (page size, margins,
header/footer references), drops media and customXml parts nothing references any more, rewrites
literal strings in headers/footers, and refuses to write a file whose body text survived.
The shipped template went from 1.5MB to 75KB this way, and every document built from it is
~650KB smaller.

`{{CLIENT}}` in the footer's confidentiality line is substituted per build by
`build-doc.sh --client "Acme"`. Build without `--client` and the placeholder is what prints —
so always pass it.

Styles the template must define, because pandoc maps to them by name: `Title`, `Subtitle`,
`Author`, `Date`, `heading 1`–`heading 9`, `Body Text`, `First Paragraph`, `Compact`,
`Verbatim Char`, `Image Caption`, `Table Caption`, `Hyperlink`, and a `Table` style.

## PDF

```bash
soffice --headless -env:UserInstallation=file:///tmp/lo-builddoc \
  --convert-to pdf --outdir . document.docx
```

The `-env:UserInstallation` flag gives LibreOffice a scratch profile, so a headless run doesn't
collide with the desktop app being open. First run is slow while that profile is built.

Fonts render as whatever the *converting machine* has installed — if the template's typeface is
missing, LibreOffice silently substitutes and the PDF looks wrong while the DOCX is fine. Install
the brand fonts (see the `bigstep-branding` skill's `assets/fonts/`) on any machine that builds
PDFs.

## Troubleshooting

| Symptom | Cause |
| --- | --- |
| `![](img.png)` prints as literal text | image path unresolved — check `--resource-path` and that the PNG exists |
| Cover title looks like body text | `fenced_divs`/`attributes` missing from `--from`, or the style name doesn't exist in the template |
| Tables narrow and ragged | post-processor didn't run |
| A table row split across two pages | post-processor didn't run, or the row is genuinely taller than a page |
| Footer says `{{CLIENT}}` | built without `--client` |
| DOCX fine, PDF wrong fonts | brand fonts not installed on the build machine |
| Word repair prompt on open | hand-edited XML — rebuild from markdown |
| Output .docx is suspiciously large | template carrying unreferenced media; re-run `make_reference_docx.py` |
