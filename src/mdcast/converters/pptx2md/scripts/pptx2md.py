"""
pptx2md command-line entry point.

Thin wrapper around :func:`mdcast.converters.pptx2md.convert`. Use the package
function directly when calling this converter from Python:
    from mdcast.converters.pptx2md import convert
    convert('input.pptx', 'output.md')
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pptx2md",
        description="Convert a .pptx file to Markdown with image extraction.",
    )
    _ = parser.add_argument("input", type=str, help="Path to input .pptx file")
    _ = parser.add_argument(
        "output",
        type=str,
        nargs="?",
        default=None,
        help="Path to output .md file (default: <input_stem>.md)",
    )
    _ = parser.add_argument(
        "--asset-dir",
        dest="asset_dir",
        type=str,
        default="assets",
        help="Directory for extracted images (default: assets)",
    )
    args = parser.parse_args(argv)

    try:
        from mdcast.converters.pptx2md import convert
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Install required dependencies: pip install python-pptx Pillow",
            file=sys.stderr,
        )
        return 1

    try:
        md_path, by_page = convert(args.input, args.output, args.asset_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Error: conversion failed — {exc}", file=sys.stderr)
        return 1

    print(f"Markdown written to: {md_path}", file=sys.stderr)
    for page in sorted(by_page):
        print(f"  Page {page}: {', '.join(by_page[page])}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
