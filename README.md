# mdcast-cli

A CLI tool for converting between Markdown and Office document formats.

## Installation

```bash
pip install mdcast-cli

# Non-Windows platforms need vector-image conversion support
pip install "mdcast-cli[vector]"
```

Install from source (development mode):

```bash
git clone <repo-url>
cd mdcast-cli

pip install -e .

# Non-Windows platforms need vector-image conversion support
pip install -e ".[vector]"
```

## Usage

### `mdcast docx2md` — Word to Markdown

Convert a `.docx` file to Markdown and extract all images into an `assets/` folder.

```bash
mdcast docx2md <input.docx> [output.md] [--asset-dir <dir>]
```

- `<output.md>` is optional; defaults to the source file's name with a `.md` extension
- Extracted images go to `<output_dir>/assets/`
- Prints `{"md_path": "...", "by_page": {...}}` JSON to stdout

**Examples:**

```bash
mdcast docx2md report.docx
# → produces report.md + assets/ directory

mdcast docx2md report.docx out/report.md --asset-dir out/images
# → produces out/report.md, images in out/images/
```

### Library call

```python
from mdcast.converters.docx2md import convert

md_path, by_page = convert("input.docx", "out.md", asset_dir="assets")
# by_page == {1: ["rId4.png", ...], 2: [...], ...}
```

### `mdcast pptx2md` — PowerPoint to Markdown

Convert a `.pptx` file to Markdown, extract images into `assets/`, and preserve slide
structure, tables, and swimlane diagrams. Like `docx2md`, its output is **deterministic**
(no AI rewriting), making it suitable as a preprocessing step for knowledge-base
ingestion and RAG pipelines. See the [pptx2md README](src/mdcast/converters/pptx2md/README.md)
for details.

```bash
mdcast pptx2md <input.pptx> [output.md] [--asset-dir <dir>]
```

- `<output.md>` is optional; defaults to the source file's name with a `.md` extension
- Extracted images (and rendered swimlane diagrams) go to `<output_dir>/assets/`
- Prints `{"md_path": "...", "by_page": {...}}` JSON to stdout
- Slides containing flowcharts / swimlane diagrams are rendered to a cropped PNG via
  LibreOffice; falls back to structured text when LibreOffice is unavailable

**Examples:**

```bash
mdcast pptx2md deck.pptx
# → produces deck.md + assets/ directory

mdcast pptx2md deck.pptx out/deck.md --asset-dir out/images
# → produces out/deck.md, images in out/images/
```

### Library call

```python
from mdcast.converters.pptx2md import convert

md_path, by_page = convert("input.pptx", "out.md", asset_dir="assets")
# by_page == {1: ["page-01-img-01.png", ...], 2: [...], ...}
```

The deterministic output structure of `pptx2md` (slide boundaries, chunking strategy,
field metadata, image and encoding conventions, no-rewrite policy, etc.) is documented
in the converter's own README: see
[pptx2md README · Output specification](src/mdcast/converters/pptx2md/README.md#output-specification).

## Output contract

The `docx2md` / `pptx2md` converters produce **deterministic** output (no AI rewriting),
with a stable, reliable structure — well suited as a preprocessing step for knowledge-base
ingestion and RAG pipelines. The detailed `pptx2md` specification is in the
[pptx2md README](src/mdcast/converters/pptx2md/README.md#output-specification); for
`docx2md` see the [docx2md README](src/mdcast/converters/docx2md/README.md).

## Roadmap

- [x] `docx2md` — Word (.docx) to Markdown
- [x] `pptx2md` — PowerPoint (.pptx) to Markdown
- [x] Deterministic output contract (slide anchors, chunking strategy, field metadata, no-rewrite policy) — see each converter's README
- [x] Shared utilities and formatting helpers
      - Extracted common helpers `clean_text()`, `rel_path()` (relative-path normalization), and `prepare_asset_dir()` into `mdcast/converters/common.py`; both converters are wired to them
      - Image naming and `<!-- Slide N -->` emission are kept converter-specific (their sources differ — docx keys by `rId`/content-type, pptx by `page-XX-img-YY`/blob)
- [x] Unified CLI entry point `mdcast <format>2md ...` (both converters routed through `mdcast.cli`; legacy `pptx2md` script removed)
- [ ] `xlsx2md` — Excel (.xlsx) to Markdown (tables / multiple sheets)
- [ ] Optional speaker-notes extraction (pptx2md already documents a `python-pptx` reference implementation)
- [ ] Output validator: assert the deterministic contract (unique & monotonically increasing anchors, all image references resolvable) for CI
