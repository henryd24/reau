"""Draws the five-step strip of the "Go from app to app" joystick preset (guides/img/apps-steps*.png).

The pictures are drawings, not screenshots: a screenshot of Android Auto shows real streets, notifications and a music
library. Run it from this folder:  .venv/bin/python3 make_apps_steps.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[2] / "guides" / "img"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"

S = 2  # drawing scale
PW, PH = 300, 190  # one panel (the dash picture, 526x300, at about 57%)
GAP, MARGIN, CAP = 14, 16, 74

BG, RAIL = (26, 29, 36), (14, 16, 20)
MAP_BG, ROAD = (36, 42, 54), (84, 92, 108)
RING, TEXT, DIM = (190, 200, 255), (236, 238, 245), (150, 156, 170)
WAZE, SPOT, GREY, GREEN = (51, 195, 255), (30, 215, 96), (70, 74, 86), (28, 40, 34)

TEXTS = {
    "en": {
        "title": "Go from app to app: navigation, Spotify and back",
        "steps": [
            ("1", "Left", "the focus appears on the apps button"),
            ("2", "Left, left", "past the microphone, on Spotify's icon"),
            ("3", "Confirm", "Spotify opens; left and right pick a card, Confirm plays"),
            ("4", "Up", "the focus leaves the app for the side bar"),
            ("5", "Left, Confirm", "Waze's icon, then the map is back"),
        ],
        "tabs": ["Home", "Recent", "Explore", "Library"],
        "note": "Drawings, not screenshots. Dash media mode with the \"Go from app to app\" preset.",
    },
    "es": {
        "title": "Pasar de app en app: navegación, Spotify y de vuelta",
        "steps": [
            ("1", "Izquierda", "el foco aparece en el botón de apps"),
            ("2", "Izquierda, izquierda", "pasa el micrófono y llega al icono de Spotify"),
            ("3", "Confirmar", "se abre Spotify; izquierda y derecha eligen tarjeta, Confirmar reproduce"),
            ("4", "Arriba", "el foco sale de la app hacia la barra lateral"),
            ("5", "Izquierda, Confirmar", "el icono de Waze, y vuelve el mapa"),
        ],
        "tabs": ["Inicio", "Recientes", "Explorar", "Biblioteca"],
        "note": "Dibujos, no capturas. Modo multimedia del tablero con el preset \"Pasar de app en app\".",
    },
}


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size * S)


def rr(d, box, r, fill=None, outline=None, width=1):
    x0, y0, x1, y1 = [v * S for v in box]
    d.rounded_rectangle((x0, y0, x1, y1), r * S, fill=fill, outline=outline, width=width * S)


def circle(d, cx, cy, r, fill=None, outline=None, width=1):
    d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=fill, outline=outline, width=width * S)


RAIL_Y = {"waze": 46, "spotify": 88, "mic": 130, "apps": 168}


def rail(d, ring):
    rr(d, (0, 0, 52, PH), 0, fill=RAIL)
    circle(d, 26, RAIL_Y["waze"], 15, fill=WAZE)
    circle(d, 26, RAIL_Y["spotify"], 15, fill=SPOT)
    circle(d, 26, RAIL_Y["mic"], 7, fill=TEXT)
    for i in range(3):
        for j in range(3):
            circle(d, 20 + i * 6, RAIL_Y["apps"] - 6 + j * 6, 1.6, fill=TEXT)
    if ring:
        circle(d, 26, RAIL_Y[ring], 19, outline=RING, width=2)


def map_view(d):
    rr(d, (56, 4, PW - 4, PH - 4), 8, fill=MAP_BG)
    for (a, b, c, e) in [(56, 130, 296, 60), (120, 186, 190, 4), (230, 186, 250, 4), (56, 80, 296, 110)]:
        d.line((a * S, b * S, c * S, e * S), fill=ROAD, width=3 * S)
    circle(d, 170, 140, 6, fill=(230, 70, 70))


def spotify_view(d, ring_card, tabs):
    rr(d, (56, 4, PW - 4, PH - 4), 8, fill=(22, 24, 28))
    for i, label in enumerate(tabs):
        d.text(((74 + i * 56) * S, 14 * S), label, fill=TEXT if i == 0 else DIM, font=font(8))
    for i in range(2):
        x0 = 72 + i * 100
        rr(d, (x0, 40, x0 + 86, 126), 6, fill=GREEN if i == 0 else GREY)
        rr(d, (x0, 134, x0 + 86, 144), 3, fill=(90, 94, 106))
        rr(d, (x0, 150, x0 + 56, 158), 3, fill=(60, 64, 74))
        if i == ring_card:
            rr(d, (x0 - 4, 36, x0 + 90, 162), 8, outline=RING, width=2)


def panel(n, tabs):
    img = Image.new("RGB", (PW * S, PH * S), BG)
    d = ImageDraw.Draw(img)
    if n == 3:
        rail(d, None)
        spotify_view(d, 0, tabs)
    elif n == 4:
        rail(d, "spotify")
        spotify_view(d, -1, tabs)
    else:
        rail(d, {1: "apps", 2: "spotify", 5: "waze"}[n])
        map_view(d)
    return img


def strip(lang):
    t = TEXTS[lang]
    w = MARGIN * 2 + 5 * PW + 4 * GAP
    h = 44 + PH + CAP + 28
    img = Image.new("RGB", (w * S, h * S), (18, 20, 25))
    d = ImageDraw.Draw(img)
    d.text((MARGIN * S, 14 * S), t["title"], fill=TEXT, font=font(15, bold=True))
    for i, (num, keys, what) in enumerate(t["steps"]):
        x = MARGIN + i * (PW + GAP)
        img.paste(panel(i + 1, t["tabs"]), (x * S, 44 * S))
        y = 44 + PH + 10
        circle(d, x + 11, y + 11, 11, fill=RING)
        d.text(((x + 11) * S, (y + 11) * S), num, fill=(18, 20, 25), font=font(12, bold=True), anchor="mm")
        d.text(((x + 28) * S, (y + 3) * S), keys, fill=TEXT, font=font(12, bold=True))
        wrap(d, what, x, y + 26, PW)
    d.text((MARGIN * S, (h - 22) * S), t["note"], fill=DIM, font=font(10))
    return img.resize((w * 3 // 2, h * 3 // 2), Image.LANCZOS)


def wrap(d, text, x, y, width):
    line, lines = "", []
    f = font(10)
    for word in text.split():
        trial = f"{line} {word}".strip()
        if d.textlength(trial, font=f) > width * S:
            lines.append(line)
            line = word
        else:
            line = trial
    lines.append(line)
    for k, ln in enumerate(lines):
        d.text((x * S, (y + k * 14) * S), ln, fill=DIM, font=f)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for lang, name in (("en", "apps-steps.png"), ("es", "apps-steps.es.png")):
        strip(lang).save(OUT / name)
        print("wrote", OUT / name)
