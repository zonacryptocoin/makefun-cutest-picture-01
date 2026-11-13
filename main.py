"""make.fun bounty cutest-picture-01: draw one cute picture, deterministically.

Spec: Python 3.13, stdlib only, no network. Writes one PNG to
/output/entry.png, <=1 MiB, <=1024x1024 px. Run twice, same bytes.
Local test: ENTRY_OUTPUT env overrides the output path.

Art: a cute kitten face — big round head, triangle ears with pink
inners, huge shiny eyes, tiny pink nose, blush cheeks, whiskers, and
a little bow — on a soft pastel background with polka dots. All shapes
are drawn pixel by pixel with fixed coordinates (no randomness).
Pure stdlib PNG encoder (zlib + CRC32), no image libraries.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
OUT = os.environ.get("ENTRY_OUTPUT", "/output/entry.png")

# Palette (soft pastel).
CREAM = (255, 250, 240)
CREAM_DARK = (238, 222, 205)
PINK = (255, 183, 197)
PINK_DEEP = (255, 140, 165)
BLUSH = (255, 170, 185)
DARK = (58, 42, 42)
WHITE = (255, 255, 255)
BOW = (255, 110, 140)
WHISKER = (150, 130, 120)


class Canvas:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def circle(self, cx, cy, r, color):
        r2 = r * r
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int(math.sqrt(max(0, r2 - dy * dy)))
            for x in range(cx - dx, cx + dx + 1):
                self.set(x, y, color)

    def ring(self, cx, cy, r, t, color):
        for a in range(0, 360):
            rad = math.radians(a)
            for k in range(t):
                x = int(cx + (r - k) * math.cos(rad))
                y = int(cy + (r - k) * math.sin(rad))
                self.set(x, y, color)

    def triangle(self, p1, p2, p3, color):
        (x1, y1), (x2, y2), (x3, y3) = p1, p2, p3
        minx, maxx = min(x1, x2, x3), max(x1, x2, x3)
        miny, maxy = min(y1, y2, y3), max(y1, y2, y3)
        den = (y2 - y3) * (x1 - x3) + (x3 - x2) * (y1 - y3)
        if den == 0:
            return
        for y in range(miny, maxy + 1):
            for x in range(minx, maxx + 1):
                a = ((y2 - y3) * (x - x3) + (x3 - x2) * (y - y3)) / den
                b = ((y3 - y1) * (x - x3) + (x1 - x3) * (y - y3)) / den
                c = 1 - a - b
                if a >= 0 and b >= 0 and c >= 0:
                    self.set(x, y, color)

    def line(self, x1, y1, x2, y2, color, width=1):
        dx, dy = x2 - x1, y2 - y1
        steps = max(abs(dx), abs(dy), 1)
        for i in range(steps + 1):
            x = int(x1 + dx * i / steps)
            y = int(y1 + dy * i / steps)
            for wx in range(-width // 2, width // 2 + 1):
                for wy in range(-width // 2, width // 2 + 1):
                    self.set(x + wx, y + wy, color)

    def arc(self, cx, cy, r, a0, a1, color, width=1):
        a = a0
        while a <= a1:
            rad = math.radians(a)
            x = int(cx + r * math.cos(rad))
            y = int(cy + r * math.sin(rad))
            for wx in range(-width // 2, width // 2 + 1):
                for wy in range(-width // 2, width // 2 + 1):
                    self.set(x + wx, y + wy, color)
            a += 1


def render():
    cv = Canvas(W, H)
    # Background: soft vertical gradient, pink to cream.
    for y in range(H):
        f = y / (H - 1)
        top = (255, 214, 224)
        bot = (255, 246, 236)
        col = tuple(int(top[i] + (bot[i] - top[i]) * f) for i in range(3))
        for x in range(W):
            cv.set(x, y, col)
    # Polka dots, fixed positions.
    dots = [(120, 120), (904, 140), (160, 880), (880, 860), (512, 90),
            (80, 520), (950, 500), (300, 160), (720, 150), (250, 940),
            (760, 930), (512, 970)]
    for (dx, dy) in dots:
        cv.circle(dx, dy, 16, WHITE)
    # Ears (behind the head).
    cv.triangle((250, 400), (330, 180), (430, 380), CREAM)
    cv.triangle((594, 380), (694, 180), (774, 400), CREAM)
    cv.triangle((295, 360), (335, 235), (395, 350), PINK)
    cv.triangle((629, 350), (689, 235), (729, 360), PINK)
    # Head.
    cv.circle(512, 580, 310, CREAM_DARK)
    cv.circle(512, 575, 300, CREAM)
    # Blush cheeks.
    cv.circle(330, 660, 48, BLUSH)
    cv.circle(694, 660, 48, BLUSH)
    # Eyes: big, shiny.
    for ex in (400, 624):
        cv.circle(ex, 520, 46, DARK)
        cv.circle(ex - 14, 505, 15, WHITE)
        cv.circle(ex + 12, 535, 7, WHITE)
    # Nose: tiny pink triangle.
    cv.triangle((492, 615), (532, 615), (512, 640), PINK_DEEP)
    # Mouth: two little arcs under the nose.
    cv.arc(482, 645, 28, 15, 165, DARK, width=5)
    cv.arc(542, 645, 28, 15, 165, DARK, width=5)
    # Whiskers.
    for (x1, y1, x2, y2) in [
            (230, 600, 120, 580), (230, 640, 115, 640), (230, 680, 125, 700),
            (794, 600, 904, 580), (794, 640, 909, 640), (794, 680, 899, 700)]:
        cv.line(x1, y1, x2, y2, WHISKER, width=4)
    # Bow on the right ear.
    cv.triangle((700, 300), (640, 250), (640, 350), BOW)
    cv.triangle((700, 300), (760, 250), (760, 350), BOW)
    cv.circle(700, 300, 18, PINK_DEEP)
    return cv


def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    return c + struct.pack(">I", binascii.crc32(typ + data) & 0xFFFFFFFF)


def write_png(path, cv):
    w, h = cv.w, cv.h
    rows = []
    for y in range(h):
        rows.append(b"\x00" + bytes(cv.px[y * w * 3:(y + 1) * w * 3]))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    idat = zlib.compress(b"".join(rows), 9)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", idat) + _chunk(b"IEND", b""))
    out_dir = os.path.dirname(path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png)


def main():
    write_png(OUT, render())


if __name__ == "__main__":
    main()
