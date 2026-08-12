"""Unit tests for ``_clean_text`` from docx2md converter."""

import sys
from mdcast.converters.docx2md.converter import _clean_text  # pyright: ignore[reportPrivateUsage]


_CASES = [
    ("cell soft wrap", "消息通知\n对象", "消息通知 对象"),
    ("crlf", "a\r\nb", "a b"),
    ("cr only", "a\rb", "a b"),
    ("trailing newline", "hello\n", "hello"),
    ("control + newline", "x\u0001\ny", "x y"),
    ("nested tabs/space collapse", "a  \n  b", "a b"),
]


def test_clean_text_cases():
    for name, src, exp in _CASES:
        got = _clean_text(src)
        assert got == exp, f"[{name}] expected {exp!r}, got {got!r}"


def main() -> None:
    ok = True
    for name, src, exp in _CASES:
        got = _clean_text(src)
        status = "ok" if got == exp else "FAIL"
        if got != exp:
            ok = False
        print(f"[{status}] {name}: {src!r} -> {got!r} (expect {exp!r})")
    print("ALL PASS" if ok else "SOME FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
