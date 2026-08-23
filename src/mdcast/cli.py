"""mdcast CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys


def _cmd_docx2md(args: argparse.Namespace) -> None:
    """Handle ``mdcast docx2md`` sub-command."""
    try:
        from mdcast.converters.docx2md import convert
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Install required dependencies: pip install python-docx Pillow",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output_path, by_page = convert(args.input, args.output, args.asset_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: conversion failed — {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Output written to: {output_path}", file=sys.stderr)
    print(json.dumps({"md_path": str(output_path), "by_page": by_page}))


def _cmd_pptx2md(args: argparse.Namespace) -> None:
    """Handle ``mdcast pptx2md`` sub-command."""
    try:
        from mdcast.converters.pptx2md import convert
    except ImportError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        print(
            "Install required dependencies: pip install python-pptx Pillow",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        output_path, by_page = convert(args.input, args.output, args.asset_dir)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"Error: conversion failed — {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Output written to: {output_path}", file=sys.stderr)
    print(json.dumps({"md_path": str(output_path), "by_page": by_page}))


def main(argv: list[str] | None = None) -> None:
    """Main CLI entry point (console_scripts: ``mdcast``)."""
    parser = argparse.ArgumentParser(
        prog="mdcast",
        description="Convert between Markdown and office document formats.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- docx2md ---
    d2m = sub.add_parser(
        "docx2md",
        help="Convert Word (.docx) to Markdown with image extraction",
    )
    _ = d2m.add_argument("input", type=str, help="Path to input .docx file")
    _ = d2m.add_argument(
        "output",
        type=str,
        nargs="?",
        default=None,
        help="Path to output .md file (default: <input_stem>.md)",
    )
    _ = d2m.add_argument(
        "--asset-dir",
        type=str,
        default=None,
        help="Directory for extracted images (default: <output_dir>/assets/)",
    )
    d2m.set_defaults(func=_cmd_docx2md)

    # --- pptx2md ---
    p2m = sub.add_parser(
        "pptx2md",
        help="Convert PowerPoint (.pptx) to Markdown with image extraction",
    )
    _ = p2m.add_argument("input", type=str, help="Path to input .pptx file")
    _ = p2m.add_argument(
        "output",
        type=str,
        nargs="?",
        default=None,
        help="Path to output .md file (default: <input_stem>.md)",
    )
    _ = p2m.add_argument(
        "--asset-dir",
        type=str,
        default=None,
        help="Directory for extracted images (default: <output_dir>/assets/)",
    )
    p2m.set_defaults(func=_cmd_pptx2md)

    args = parser.parse_args(argv)
    args.func(args)
