# docx2md Converter

Convert Word `.docx` files to Markdown while extracting all images into an
`assets/` folder. Preserves heading hierarchy, lists, tables, inline formatting
(bold, italic, code), and reading order.

## When to use

- Turn a `.docx` into `.md` + images for editing, search, archiving, or restyling
- Preprocessing for knowledge-base / RAG ingestion (deterministic structure — see the output contract below)

**Do not** use for: translating documents, modifying the original `.docx`, or
converting `.pdf` / `.pptx` files.

## Quick start

### CLI

```bash
mdcast docx2md <input.docx> [output.md] [--asset-dir <dir>]
```

- `<output.md>` is optional; defaults to the source file's stem with `.md`
- Extracted images go to `<output_dir>/assets/`; old contents are removed first
- stdout prints `{"md_path": "...", "by_page": {...}}` JSON; stderr prints status

### Library

```python
from mdcast.converters.docx2md import convert

md_path, by_page = convert("input.docx", "out.md", asset_dir="assets")
# by_page == {1: ["rId4.png", ...], 2: [...], ...}
```

## How it works

### 1. Item extraction

The converter walks `Document.paragraphs`, `Document.tables`, and inline
shapes, extracting these item types:

| Item type | What happens |
|-----------|-------------|
| **Heading** (style `Heading N`) | Rendered as `#` / `##` etc. — preserves hierarchy |
| **Paragraph** | Plain text with inline formatting converted to Markdown (`**bold**`, `*italic*`, `` `code` ``) |
| **List** (bulleted / numbered) | Rendered as proper Markdown list syntax with nesting |
| **Table** | Cell text extracted row-by-row, rendered as a GFM Markdown table |
| **Inline image** | Extracted to `assets/rIdX.ext` |
| **Page break** | Rendered as a `---` horizontal rule |

### 2. Image extraction

Each inline shape / picture is written to `assets/rId<number>.<ext>` with a
relative reference in the Markdown output. Master/header/footer images are
excluded.

EMF/WMF vector images are converted to PNG automatically:
- **Windows**: rendered via the built-in GDI API (no extra package needed)
- **Other platforms**: install `PyMuPDF` to convert.
  If no converter is available, the vector file is left as-is and the reference
  is still emitted (but may not render in all viewers)

### 3. Text cleaning

Word documents frequently contain invisible control characters. All extracted
text passes through a cleaning pass:

| Character | Treatment |
|-----------|-----------|
| `U+000B` (vertical tab) | Replaced with space |
| `U+000C` (form feed) | Replaced with space |
| `U+00A0` (non-breaking space) | Replaced with space |
| C0 controls (except `\n\r\t`) | Removed |
| C1 controls (`U+0080–U+009F`) | Removed |
| Unicode format chars (`U+200B–U+200F`, `U+2028–U+202F`, `U+FEFF`) | Removed |
| Multiple consecutive spaces | Collapsed to one |

### 4. Reading order & headings

Items are processed in document order (the natural reading order of a Word
document). The highest-level heading becomes the document title (`#`), with
subsequent headings rendered at their appropriate level (`##` → `###` etc.).

## Dependencies

```bash
# Base install
pip install mdcast-cli

# Non-Windows platforms need vector conversion support
pip install "mdcast-cli[vector]"
```

- **Required**: `python-docx`, `Pillow`
- **Optional** (`[vector]` extras): `PyMuPDF` — for EMF/WMF → PNG conversion on non-Windows platforms

## Output contract

Downstream tools (knowledge-base ingestion, RAG pipelines, search indexing) can
rely on the following deterministic output structure.

### File encoding

- **UTF-8 without BOM**
- Line endings: `\n` (LF)

### Section structure

Every heading in the document produces a section delimited by a `<!-- Page N -->`
anchor comment:

```markdown
<!-- Page 1 -->
# Document Title

Content for the first section…

<!-- Page 2 -->
## First Heading

Content for the second section…
```

**Rules:**
- `#` (H1) is used for the document title (Word "Title" style or "Heading 1")
- `##`–`######` (H2–H6) map directly to Word "Heading 2"–"Heading 6" styles
- Each heading increments the page counter by 1
- Non-heading content belongs to the preceding heading's section

### Inline formatting

| Word Formatting | Markdown Output |
|-----------------|-----------------|
| **Bold** | `**bold text**` |
| *Italic* | `*italic text*` |
| Bold + Italic | `***bold italic***` |
| `Courier New` font | `` `inline code` `` |
| Hyperlink | `[link text](url)` |

### Lists

**Bulleted lists:**

```markdown
- Item level 1
  - Item level 2
    - Item level 3
```

**Numbered lists:**

```markdown
1. First item
1. Second item
   1. Nested item
```

### Tables

Tables are rendered as GitHub Flavored Markdown tables:

```markdown
| Header 1 | Header 2 |
|----------|----------|
| Cell 1   | Cell 2   |
```

**Rules:**
- Column widths are padded to align with the widest cell per column
- Empty cells are represented as empty strings
- Trailing blank rows are dropped

### Images

- Extracted to the `assets/` directory next to the output `.md` file
- Referenced with relative paths: `![alt](assets/rIdX.png)`
- Naming: `rId<number>.<ext>` (as extracted from the Word document's image relationships)
- Supported formats: PNG, JPEG, GIF, BMP, TIFF, EMF, WMF, SVG

### Text cleaning

All extracted text is cleaned of invisible control characters:

| Character | Replacement |
|-----------|-------------|
| U+000B (vertical tab) | Space |
| U+000C (form feed) | Space |
| U+00A0 (non-breaking space) | Space |
| C0 controls (except `\n\r\t`) | Removed |
| C1 controls (U+0080–U+009F) | Removed |
| Unicode format characters | Removed |
| Multiple consecutive spaces | Collapsed to one |

### No AI rewriting

The output is a **faithful** extraction of the original Word document's text.
No summarization, rephrasing, or content generation is performed.
