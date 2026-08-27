import random
import string

# Excludes visually-ambiguous characters (0/O, 1/I/L) so a human reading the
# distorted SVG never has to guess between two valid-looking answers.
_ALPHABET = "".join(c for c in string.ascii_uppercase + string.digits if c not in "0O1IL")
_COLORS = ["#1558e0", "#7c3aed", "#e11d48", "#0f766e", "#c2410c", "#334155"]


def generate_captcha_code(length: int = 5) -> str:
    return "".join(random.choices(_ALPHABET, k=length))


def render_captcha_svg(code: str, width: int = 160, height: int = 56) -> str:
    """Renders the code as an SVG with per-character rotation/jitter plus
    line and dot noise — enough distortion that a script reading the raw
    response has to actually do image analysis, not just read text."""
    char_w = width / len(code)
    chars_svg = []
    for i, ch in enumerate(code):
        x = char_w * i + char_w / 2 + random.uniform(-4, 4)
        y = height / 2 + random.uniform(-6, 6)
        rotate = random.uniform(-25, 25)
        color = random.choice(_COLORS)
        size = random.randint(26, 32)
        chars_svg.append(
            f'<text x="{x:.1f}" y="{y:.1f}" transform="rotate({rotate:.1f} {x:.1f} {y:.1f})" '
            f'font-size="{size}" font-family="Verdana, sans-serif" font-weight="bold" '
            f'fill="{color}" text-anchor="middle" dominant-baseline="middle">{ch}</text>'
        )

    noise_lines = [
        f'<line x1="{random.uniform(0, width):.1f}" y1="{random.uniform(0, height):.1f}" '
        f'x2="{random.uniform(0, width):.1f}" y2="{random.uniform(0, height):.1f}" '
        f'stroke="#cbd5e1" stroke-width="1.5" />'
        for _ in range(6)
    ]
    noise_dots = [
        f'<circle cx="{random.uniform(0, width):.1f}" cy="{random.uniform(0, height):.1f}" r="1" fill="#94a3b8" />'
        for _ in range(30)
    ]

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-label="CAPTCHA challenge">'
        f'<rect width="{width}" height="{height}" fill="#f1f5f9" rx="8" />'
        + "".join(noise_lines)
        + "".join(noise_dots)
        + "".join(chars_svg)
        + "</svg>"
    )
