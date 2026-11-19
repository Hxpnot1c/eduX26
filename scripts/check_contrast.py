"""Check the web pages' colour tokens (edux/web/static/css/tokens.css) against WCAG 2.2 and for the levels' legibility.

    python scripts/check_contrast.py

For each scheme (light, dark) it checks: ink, muted text and the accent against the paper (text, AA 4.5:1, ink 7:1);
each level's ring against the paper (non-text, 3:1); neighbouring level fills against each other (at least 1.4:1, so the
three levels stay distinguishable in greyscale and under colour-blindness, where hue is lost and luminance remains); and
that the three levels differ in greyscale by a margin. Exits 1 on any failure. tests/test_web_design.py runs it."""

from __future__ import annotations

import re
import sys
from pathlib import Path

TOKENS = Path(__file__).resolve().parent.parent / "edux" / "web" / "static" / "css" / "tokens.css"


def _hex(value: str) -> tuple[float, float, float]:
    value = value.strip().lstrip("#")
    return tuple(int(value[i : i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]


def luminance(value: str) -> float:
    def channel(c: float) -> float:
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in _hex(value))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a: str, b: str) -> float:
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def schemes(css: str) -> dict[str, dict[str, str]]:
    """Token values for the light scheme (:root) and the dark scheme (the data-theme dark block)."""
    blocks = {
        "light": re.search(r":root \{(.*?)\n\}", css, re.S),
        "dark": re.search(r':root\[data-theme="dark"\] \{(.*?)\n\}', css, re.S),
    }
    out = {}
    for name, match in blocks.items():
        assert match, f"no {name} block in tokens.css"
        out[name] = dict(re.findall(r"--([a-z-]+):\s*(#[0-9a-fA-F]{6})", match.group(1)))
    out["dark"] = {**{k: v for k, v in out["light"].items()}, **out["dark"]}
    return out


def check_scheme(scheme: str, t: dict[str, str]) -> list[str]:
    problems: list[str] = []

    def need(label: str, a: str, b: str, minimum: float) -> None:
        got = ratio(t[a], t[b])
        if got < minimum:
            problems.append(f"{scheme}: {label} {t[a]} on {t[b]} is {got:.2f}:1, needs {minimum}:1")

    need("ink on paper", "ink", "paper", 7.0)
    need("muted text on paper", "muted", "paper", 4.5)
    need("muted text on sunk paper", "muted", "paper-sunk", 4.5)
    need("accent on paper", "accent", "paper", 4.5)
    for level in ("new", "developing", "secure"):
        need(f"{level} ring on paper", f"lv-{level}-ring", "paper", 3.0)
    need("new fill against developing fill", "lv-new-fill", "lv-developing-fill", 1.4)
    need("developing fill against secure fill", "lv-developing-fill", "lv-secure-fill", 1.4)
    ls = [luminance(t[f"lv-{lv}-fill"]) for lv in ("new", "developing", "secure")]
    if not (ls[0] > ls[1] > ls[2] or ls[0] < ls[1] < ls[2]):
        problems.append(f"{scheme}: the level fills are not in order of luminance, so greyscale loses the order")
    return problems


def check(css: str | None = None) -> list[str]:
    problems: list[str] = []
    for scheme, tokens in schemes(css if css is not None else TOKENS.read_text(encoding="utf-8")).items():
        problems += check_scheme(scheme, tokens)
    return problems


def main() -> int:
    problems = check()
    for p in problems:
        print("FAIL", p)
    print("contrast: ok" if not problems else f"contrast: {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
