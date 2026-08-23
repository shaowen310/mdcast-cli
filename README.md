# mdcast-cli

CLI 工具，用于在 Markdown 与 Office 文档格式之间互相转换。

## 安装

```bash
pip install mdcast-cli

# 非 Windows 平台需要矢量图转换支持
pip install "mdcast-cli[vector]"
```

从源码安装（开发模式）：

```bash
git clone <repo-url>
cd mdcast-cli
pip install -e ".[vector]"
```

## 用法

### `mdcast docx2md` — Word 转 Markdown

将 `.docx` 文件转换为 Markdown，同时提取所有图片到 `assets/` 文件夹。

```bash
mdcast docx2md <input.docx> [output.md] [--asset-dir <dir>]
```

- `<output.md>` 可选，默认为输入文件同名 `.md`
- 提取的图片放在 `<output_dir>/assets/`
- stdout 输出 `{"md_path": "...", "by_page": {...}}` JSON

**示例：**

```bash
mdcast docx2md report.docx
# → 生成 report.md + assets/ 目录

mdcast docx2md report.docx out/report.md --asset-dir out/images
# → 生成 out/report.md，图片放在 out/images/
```

### 库函数调用

```python
from mdcast.converters.docx2md import convert

md_path, by_page = convert("input.docx", "out.md", asset_dir="assets")
# by_page == {1: ["rId4.png", ...], 2: [...], ...}
```

### `mdcast pptx2md` — PowerPoint 转 Markdown

将 `.pptx` 文件转换为 Markdown，提取图片到 `assets/`，并保留幻灯片结构、
表格与泳道图。与 `docx2md` 同构，输出同样**确定性**（不做 AI 改写），
适合作为知识库摄入、RAG 流水线的预处理步骤。详见
[pptx2md README](src/mdcast/converters/pptx2md/README.md)。

```bash
mdcast pptx2md <input.pptx> [output.md] [--asset-dir <dir>]
```

- `<output.md>` 可选，默认为输入文件同名 `.md`
- 提取的图片（及泳道图渲染图）放在 `<output_dir>/assets/`
- stdout 输出 `{"md_path": "...", "by_page": {...}}` JSON
- 含流程图/泳道图的幻灯片会调用 LibreOffice 渲染为裁剪后的 PNG；无 LibreOffice
  时回退为结构化文本

**示例：**

```bash
mdcast pptx2md deck.pptx
# → 生成 deck.md + assets/ 目录

mdcast pptx2md deck.pptx out/deck.md --asset-dir out/images
# → 生成 out/deck.md，图片放在 out/images/
```

### 库函数调用

```python
from mdcast.converters.pptx2md import convert

md_path, by_page = convert("input.pptx", "out.md", asset_dir="assets")
# by_page == {1: ["page-01-img-01.png", ...], 2: [...], ...}
```

## 输出契约

docx2md / pptx2md 转换器提供**确定性**输出（不做 AI 改写），输出结构稳定可靠，适合作为知识库摄入、RAG 流水线的预处理步骤。详见 [docx2md README](src/mdcast/converters/docx2md/README.md) 与 [pptx2md README](src/mdcast/converters/pptx2md/README.md)。

## Roadmap

- [x] `docx2md` — Word (.docx) 转 Markdown
- [x] `pptx2md` — PowerPoint (.pptx) 转 Markdown
- [ ] `md2docx` — Markdown 转 Word (.docx)
- [ ] 共享工具与格式辅助函数
