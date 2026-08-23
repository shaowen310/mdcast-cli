"""Shared utilities for the mdcast ``*2md`` converters.

Holds formatting/IO helpers that were previously duplicated across the
individual converters (``docx2md``, ``pptx2md``): text sanitisation, POSIX-style
relative-path computation for Markdown image references, and asset-directory
preparation. Centralising them keeps the deterministic output contract
consistent across converters.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

# C0 control chars except \n, \r, \t (U+0009 is kept; U+000A/U+000D are handled
# separately when keep_newlines is False) plus C1 control chars.
_CONTROL_RE = re.compile(r"[\u0000-\u0008\u000b\u000c\u000e-\u001f\u007f\u0080-\u009f]")
_FORMAT_CHARS_RE = re.compile(r"[\u200b-\u200f\u2028-\u202f\ufeff]")


def clean_text(text: str, *, keep_newlines: bool = False) -> str:
    """Remove invisible / control characters and normalise whitespace.

    Word exposes soft line breaks and cell wraps as literal ``\\n`` / ``\\r``
    characters, which split a Markdown table row (or any block) across several
    physical lines. For those cases pass ``keep_newlines=False`` so newlines
    collapse to spaces (the ``docx2md`` behaviour). PowerPoint manual line
    breaks should be preserved, so ``pptx2md`` passes ``keep_newlines=True``.

    Both modes:
    - ``U+000B`` (vertical tab), ``U+000C`` (form feed), ``U+00A0``
      (non-breaking space) → regular space
    - C0 / C1 control chars and Unicode format chars → stripped
    - leading/trailing whitespace trimmed
    """
    if not text:
        return ""
    text = text.replace("\u000b", " ").replace("\u000c", " ").replace("\u00a0", " ")

    if not keep_newlines:
        # Collapse Word line breaks / cell soft wraps to spaces so they never
        # break a Markdown table row onto multiple physical lines.
        text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

    text = _CONTROL_RE.sub("", text)
    text = _FORMAT_CHARS_RE.sub("", text)
    # keep_newlines=True preserves \n/\r and only collapses runs of spaces/tabs;
    # otherwise collapse runs of spaces.
    text = re.sub(r"[ \t]+" if keep_newlines else r"  +", " ", text)
    return text.strip()


def rel_path(base: str | os.PathLike[str], target: str | os.PathLike[str]) -> str:
    """Return a POSIX-style relative path from *base* to *target*.

    Markdown image references require forward slashes, but ``os.path.relpath``
    on Windows emits backslashes. This normalises the result so image links
    work consistently across platforms.
    """
    return os.path.relpath(target, base).replace("\\", "/")


def prepare_asset_dir(asset_dir: Path) -> None:
    """Prepare *asset_dir* for a deterministic re-run.

    Removes existing files (but leaves the directory in place) and ensures the
    directory exists. Both converters clear only files, never nested
    subdirectories, so this matches their prior behaviour.
    """
    if asset_dir.exists():
        for f in asset_dir.iterdir():
            if f.is_file():
                f.unlink()
    else:
        asset_dir.mkdir(parents=True, exist_ok=True)
