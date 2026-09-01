"""
Generates SVG sign cards for ISL alphabets (A-Z), numbers (0-9),
and common words. Each card shows the letter/word with a hand-shape
visual hint rendered in SVG.
"""

import os
import json

SIGNS_DIR = os.path.join(os.path.dirname(__file__), "backend", "static", "signs")

# ── Colour palette ────────────────────────────────────────────────────────────
SKIN   = "#F4C89A"
DARK   = "#C8945A"
NAIL   = "#E8A080"
BG     = "#1a1a2e"
CARD   = "#16213e"
ACCENT = "#0f3460"
GOLD   = "#e94560"

# ── SVG template helper ───────────────────────────────────────────────────────
def make_svg(label: str, hand_path: str, color: str = GOLD) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="160" height="200" viewBox="0 0 160 200">
  <defs>
    <radialGradient id="bg" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1e3a5f"/>
      <stop offset="100%" stop-color="#0a0a1a"/>
    </radialGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="160" height="200" rx="16" fill="url(#bg)" stroke="{color}" stroke-width="2"/>
  <!-- Hand shape -->
  <g transform="translate(80,90)" filter="url(#glow)">
    {hand_path}
  </g>
  <!-- Label -->
  <text x="80" y="175" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="28" font-weight="bold" fill="{color}">{label}</text>
  <!-- ISL tag -->
  <text x="80" y="195" text-anchor="middle" font-family="Arial,sans-serif"
        font-size="9" fill="#88aacc">Indian Sign Language</text>
</svg>"""

# ── Hand shape SVG paths per letter ──────────────────────────────────────────
# Each entry is an SVG fragment drawn relative to (0,0) center
def palm(fingers="11111", rotate=0) -> str:
    """Quick palm + 5 fingers. fingers='01011' means index+ring up."""
    f = list(fingers)
    parts = []
    # Palm
    parts.append(f'<ellipse cx="0" cy="20" rx="28" ry="32" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>')
    # Thumb
    parts.append(f'<ellipse cx="-32" cy="10" rx="10" ry="16" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-20,-32,10)"/>')
    # Four fingers
    xs = [-18, -6, 6, 18]
    labels = [f[1], f[2], f[3], f[4]]
    for x, up in zip(xs, labels):
        h = 40 if up == "1" else 18
        y_base = -12
        parts.append(f'<rect x="{x-7}" y="{y_base-h}" width="12" height="{h+10}" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>')
        parts.append(f'<ellipse cx="{x-1}" cy="{y_base-h}" rx="6" ry="6" fill="{NAIL}"/>')
    rot = f' transform="rotate({rotate})"' if rotate else ""
    return f'<g{rot}>' + "".join(parts) + "</g>"

# Simplified distinct hand shapes for every letter
LETTER_SHAPES = {
    "A": f'<ellipse cx="0" cy="15" rx="28" ry="32" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,5)"/>'
         f'<rect x="-20" y="-30" width="11" height="20" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-7" y="-30" width="11" height="20" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="6" y="-30" width="11" height="20" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',

    "B": palm("11111"),
    "C": f'<path d="M 25,-20 A 35,40 0 1,0 25,40" fill="none" stroke="{SKIN}" stroke-width="22" stroke-linecap="round"/>',
    "D": f'<ellipse cx="0" cy="15" rx="28" ry="32" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-7" y="-50" width="12" height="45" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-1" cy="-50" rx="6" ry="6" fill="{NAIL}"/>',
    "E": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="8" rx="9" ry="12" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,8)"/>',
    "F": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="5" y="-45" width="12" height="38" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="18" y="-45" width="12" height="38" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<circle cx="10" cy="-8" r="9" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "G": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-35" y="-5" width="35" height="12" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "H": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-35" y="-8" width="35" height="11" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-35" y="5" width="35" height="11" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "I": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="8" rx="9" ry="12" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,8)"/>'
         f'<rect x="14" y="-48" width="12" height="42" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "J": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<path d="M 18,-48 L 18,10 Q 18,28 0,28" fill="none" stroke="{SKIN}" stroke-width="12" stroke-linecap="round"/>',
    "K": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="5" y="-50" width="12" height="38" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-20,11,-31)"/>',
    "L": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-42" y="8" width="36" height="12" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "M": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-10,-30,5)"/>',
    "N": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-10,-30,5)"/>',
    "O": f'<ellipse cx="0" cy="0" rx="28" ry="32" fill="none" stroke="{SKIN}" stroke-width="18"/>',
    "P": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-40,0,0)"/>',
    "Q": f'<ellipse cx="0" cy="0" rx="28" ry="32" fill="none" stroke="{SKIN}" stroke-width="18"/>'
         f'<line x1="18" y1="22" x2="32" y2="38" stroke="{SKIN}" stroke-width="10" stroke-linecap="round"/>',
    "R": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(10,0,0)"/>'
         f'<rect x="2" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-10,0,0)"/>',
    "S": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="9" ry="12" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-5,-30,5)"/>',
    "T": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-28" cy="0" rx="9" ry="12" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-20,-28,0)"/>',
    "U": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-10" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="4" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "V": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-10" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-10,-4,-28)"/>'
         f'<rect x="4" y="-50" width="12" height="44" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(10,10,-28)"/>',
    "W": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-14" y="-50" width="11" height="44" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-1" y="-50" width="11" height="44" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="12" y="-50" width="11" height="44" rx="5" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "X": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="30" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(5,0,0)"/>',
    "Y": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-42" y="0" width="36" height="12" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="14" y="-48" width="12" height="42" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "Z": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-8" y="-50" width="12" height="28" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(30,0,-36)"/>',
}

NUMBER_SHAPES = {
    "0": f'<ellipse cx="0" cy="0" rx="26" ry="32" fill="none" stroke="{SKIN}" stroke-width="18"/>',
    "1": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-6" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "2": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-12" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="2" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "3": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-18" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-4" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="10" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>',
    "4": palm("01111"),
    "5": palm("11111"),
    "6": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="3" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-24" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,5)"/>',
    "7": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-12" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="2" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,5)"/>',
    "8": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-6" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-15,-30,5)"/>',
    "9": f'<ellipse cx="0" cy="20" rx="28" ry="30" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<rect x="-6" y="-52" width="12" height="48" rx="6" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5"/>'
         f'<ellipse cx="-30" cy="5" rx="10" ry="14" fill="{SKIN}" stroke="{DARK}" stroke-width="1.5" transform="rotate(-20,-30,5)"/>',
}

# Common ISL words — rendered with descriptive label + distinct colour accent
WORD_COLORS = {
    "hello":    "#4ecdc4", "thank you": "#45b7d1", "sorry":  "#96ceb4",
    "please":   "#ffeaa7", "yes":       "#fd79a8", "no":     "#e17055",
    "help":     "#74b9ff", "water":     "#00cec9", "food":   "#fdcb6e",
    "love":     "#e84393", "good":      "#00b894", "bad":    "#d63031",
    "home":     "#6c5ce7", "school":    "#0984e3", "work":   "#e67e22",
    "name":     "#1abc9c", "india":     "#f39c12", "namaste":"#8e44ad",
    "come":     "#2ecc71", "go":        "#e74c3c", "stop":   "#c0392b",
    "welcome":  "#27ae60", "friend":    "#3498db", "family": "#9b59b6",
}

def word_shape(word: str, color: str) -> str:
    w = word.upper()
    return (
        f'<ellipse cx="0" cy="10" rx="55" ry="42" fill="{SKIN}" stroke="{color}" stroke-width="2.5"/>'
        f'<text x="0" y="16" text-anchor="middle" font-family="Arial,sans-serif" '
        f'font-size="13" font-weight="bold" fill="{color}">{w}</text>'
    )

# ── Generate files ────────────────────────────────────────────────────────────
mapping = {"alphabets": {}, "numbers": {}, "words": {}}

# Alphabets
for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
    shape = LETTER_SHAPES.get(ch, palm())
    svg = make_svg(ch, shape, GOLD)
    path = os.path.join(SIGNS_DIR, "alphabets", f"{ch}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    mapping["alphabets"][ch] = f"/static/signs/alphabets/{ch}.svg"

# Numbers
for n in "0123456789":
    shape = NUMBER_SHAPES.get(n, palm())
    svg = make_svg(n, shape, "#4ecdc4")
    path = os.path.join(SIGNS_DIR, "numbers", f"{n}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    mapping["numbers"][n] = f"/static/signs/numbers/{n}.svg"

# Words
for word, color in WORD_COLORS.items():
    shape = word_shape(word, color)
    svg = make_svg(word.upper(), shape, color)
    fname = word.replace(" ", "_")
    path = os.path.join(SIGNS_DIR, "words", f"{fname}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    mapping["words"][word.lower()] = f"/static/signs/words/{fname}.svg"

# Save mapping JSON
with open(os.path.join(os.path.dirname(__file__), "backend", "sign_mapping.json"), "w") as f:
    json.dump(mapping, f, indent=2)

print(f"Generated {len(mapping['alphabets'])} alphabets, "
      f"{len(mapping['numbers'])} numbers, "
      f"{len(mapping['words'])} word signs.")
print("sign_mapping.json saved.")
