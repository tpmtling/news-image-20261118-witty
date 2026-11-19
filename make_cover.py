"""Render the 18 November 2026 world-news cover as a single square image.

The five stories of the day live in STORIES below.  The first entry is the
cover story and gets the top half of the poster; the other four are drawn
as a two-by-two grid of tiles underneath.  Output is news_image.png,
exactly 1024 by 1024, and the rendering is fully deterministic.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "news_image.png"

SIZE = 1024
MARGIN = 46
BG = (16, 18, 30)          # near-black indigo
PANEL = (26, 29, 46)       # tile background
PANEL_LINE = (52, 56, 82)
INK = (242, 243, 248)      # main text
SOFT = (178, 182, 205)     # deck text
FAINT = (96, 101, 138)     # ghost numerals

FONT_DIR = Path("/usr/share/fonts/truetype/noto")
F_BLACK = str(FONT_DIR / "NotoSans-CondensedBlack.ttf")
F_XBOLD = str(FONT_DIR / "NotoSans-CondensedExtraBold.ttf")
F_BOLD = str(FONT_DIR / "NotoSans-CondensedBold.ttf")
F_SEMI = str(FONT_DIR / "NotoSans-CondensedSemiBold.ttf")
F_REG = str(FONT_DIR / "NotoSans-Condensed.ttf")

STORIES = [
    {
        "category": "DIPLOMACY",
        "place": "APEC SUMMIT · SHENZHEN, CHINA",
        "accent": (255, 92, 92),
        "headline": "TRUMP, XI & PUTIN SET FOR HISTORIC TRILATERAL TALKS",
        "deck": (
            "Donald Trump lands in Shenzhen for the APEC summit and Xi Jinping "
            "greets him on the tarmac, after Xi meets Vladimir Putin. Their "
            "first-ever three-way summit, set for Thursday, puts Ukraine, "
            "Iran, nuclear arms and trade on a single table."
        ),
    },
    {
        "category": "MIDDLE EAST",
        "accent": (255, 122, 89),
        "headline": "US & IRAN TRADE STRIKES OVER HORMUZ",
        "deck": (
            "US jets hit a missile site on Iran's Qeshm Island; Tehran's drones "
            "target US bases in Kuwait and Bahrain. An ADNOC ship is struck in "
            "the Strait, one crew member missing."
        ),
    },
    {
        "category": "UKRAINE WAR",
        "accent": (255, 209, 102),
        "headline": "CRIMEAN BRIDGE HIT AGAIN; EU OFFERS €45BN",
        "deck": (
            "Ukraine strikes the Kerch Bridge for a second straight day as "
            "Brussels proposes a €45 billion loan for Kyiv. Russian strikes "
            "on Odesa kill four people."
        ),
    },
    {
        "category": "GAZA & ISRAEL",
        "accent": (92, 200, 250),
        "headline": "ISRAEL OPENS NEW OPERATION IN CENTRAL GAZA",
        "deck": (
            "Troops begin a concentrated operation in three areas west of the "
            "Yellow Line. The Knesset elects Matan Kahana speaker, a win for "
            "Netanyahu's opponents."
        ),
    },
    {
        "category": "HEALTH",
        "accent": (123, 216, 143),
        "headline": "US LOSES ITS MEASLES-FREE STATUS",
        "deck": (
            "PAHO strips the US of measles elimination status as cases soar "
            "amid falling vaccination. Mexico and Bolivia lose theirs too."
        ),
    },
]


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap measured with the real font metrics."""
    lines = []
    current = ""
    for word in text.split():
        trial = word if not current else current + " " + word
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_lines(draw, text, path, start_size, max_width, max_lines, min_size=20):
    """Shrink a headline font until the wrapped text fits max_lines."""
    size = start_size
    while size > min_size:
        fnt = font(path, size)
        lines = wrap(draw, text, fnt, max_width)
        if len(lines) <= max_lines:
            return fnt, lines
        size -= 2
    fnt = font(path, min_size)
    return fnt, wrap(draw, text, fnt, max_width)


def chip(draw, x, y, label, accent):
    """Small filled category label; returns its width."""
    fnt = font(F_BOLD, 20)
    w = int(draw.textlength(label, font=fnt)) + 24
    draw.rounded_rectangle([x, y, x + w, y + 30], radius=7, fill=accent)
    draw.text((x + 12, y + 3), label, font=fnt, fill=(14, 15, 24))
    return w


def draw_cover(draw):
    story = STORIES[0]
    x = MARGIN
    y = 30
    # Masthead row.
    draw.text((x, y), "THE DAY IN ONE IMAGE", font=font(F_XBOLD, 29), fill=INK)
    tag = "WORLD NEWS COVER"
    tag_f = font(F_SEMI, 21)
    tw = draw.textlength(tag, font=tag_f)
    draw.text((SIZE - MARGIN - tw, y + 4), tag, font=tag_f, fill=SOFT)
    y += 48
    draw.line([x, y, SIZE - MARGIN, y], fill=PANEL_LINE, width=2)
    y += 20

    # Cover story: chip + place line, then the big headline.
    w = chip(draw, x, y, story["category"], story["accent"])
    draw.text(
        (x + w + 16, y + 3), story["place"], font=font(F_SEMI, 21), fill=SOFT
    )
    y += 46
    head_f, lines = fit_lines(
        draw, story["headline"], F_BLACK, 84, SIZE - 2 * MARGIN, 3, min_size=60
    )
    line_h = int(head_f.size * 1.02)
    for line in lines:
        draw.text((x, y), line, font=head_f, fill=INK)
        y += line_h
    y += 10
    deck_f = font(F_REG, 25)
    for line in wrap(draw, story["deck"], deck_f, SIZE - 2 * MARGIN):
        draw.text((x, y), line, font=deck_f, fill=SOFT)
        y += 33
    return y + 16


def draw_tile(draw, story, index, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w, y + h], radius=14, fill=PANEL)
    accent = story["accent"]
    # Ghost index numeral, top right.
    num = "%02d" % index
    num_f = font(F_BLACK, 54)
    nw = draw.textlength(num, font=num_f)
    draw.text((x + w - nw - 16, y + 10), num, font=num_f, fill=FAINT)
    inner = x + 18
    cy = y + 18
    chip(draw, inner, cy, story["category"], accent)
    cy += 44
    head_f, lines = fit_lines(draw, story["headline"], F_XBOLD, 35, w - 36, 2, min_size=27)
    for line in lines:
        draw.text((inner, cy), line, font=head_f, fill=INK)
        cy += int(head_f.size * 1.05)
    cy += 5
    # Shrink the deck font until every line fits inside the tile.
    room = y + h - 10 - cy
    for size in (20, 19, 18, 17):
        deck_f = font(F_REG, size)
        lines = wrap(draw, story["deck"], deck_f, w - 36)
        if len(lines) * (size + 5) <= room:
            break
    for line in lines:
        draw.text((inner, cy), line, font=deck_f, fill=SOFT)
        cy += size + 5


def main():
    img = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)
    grid_top = draw_cover(draw)
    draw.line([MARGIN, grid_top, SIZE - MARGIN, grid_top], fill=PANEL_LINE, width=2)

    footer_h = 52
    grid_bottom = SIZE - footer_h - 12
    gap = 16
    tile_w = (SIZE - 2 * MARGIN - gap) // 2
    tile_h = (grid_bottom - grid_top - gap) // 2
    positions = [
        (MARGIN, grid_top + 14),
        (MARGIN + tile_w + gap, grid_top + 14),
        (MARGIN, grid_top + 14 + tile_h + gap),
        (MARGIN + tile_w + gap, grid_top + 14 + tile_h + gap),
    ]
    for i, story in enumerate(STORIES[1:]):
        px, py = positions[i]
        draw_tile(draw, story, i + 1, px, py, tile_w, tile_h)

    # Footer strip.
    fy = SIZE - footer_h
    draw.line([MARGIN, fy, SIZE - MARGIN, fy], fill=PANEL_LINE, width=2)
    foot = "Wednesday, 18 November 2026  ·  THE DAY IN ONE IMAGE"
    foot_f = font(F_BOLD, 23)
    fw = draw.textlength(foot, font=foot_f)
    draw.text(((SIZE - fw) / 2, fy + 13), foot, font=foot_f, fill=INK)

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, img.size)


if __name__ == "__main__":
    main()
