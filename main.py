#!/usr/bin/env python3
"""The World Today - Friday 20 November 2026.

A make.fun news-image entry. Draws a 1024x1024 newspaper front page
summing up the world's news of Friday 20 November 2026 and writes it
as a PNG to $MAKEFUN_OUTPUT_DIR/entry.png (default /output).

Pure Python standard library: no PIL, no network, no API keys, no
randomness, no timestamps. Every glyph comes from a hand-written 5x7
bitmap font below, every icon is drawn from geometric shapes, and the
PNG encoder is written here with zlib + struct. Running the program
twice produces a byte-identical file.
"""

import math
import os
import struct
import zlib

W = 1024
H = 1024

# Palette: warm newsprint paper, dark ink, deep navy masthead.
PAPER = (247, 242, 231)
CARD = (255, 253, 246)
INK = (22, 22, 22)
MUTED = (96, 96, 96)
NAVY = (20, 38, 74)
NAVY_DARK = (13, 25, 50)
GOLD = (201, 162, 39)
RED = (179, 38, 30)
TEAL = (15, 118, 110)
SKY = (135, 190, 220)
SEA = (46, 110, 160)
GREEN = (46, 125, 60)
ORANGE = (224, 122, 26)
YELLOW = (242, 201, 60)
WHITE = (255, 255, 255)
GREY_LINE = (190, 184, 170)


class Canvas:
    """A tiny RGB framebuffer with shape helpers and a PNG writer."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.rect(0, 0, w, h, bg)

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = color[0]
                self.buf[i + 1] = color[1]
                self.buf[i + 2] = color[2]

    def hline(self, x, y, w, color, t=1):
        for k in range(t):
            self.rect(x, y + k, w, 1, color)

    def vline(self, x, y, h, color, t=1):
        for k in range(t):
            self.rect(x + k, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        """Bresenham line, optionally thickened by t pixels."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.rect(x - t // 2, y - t // 2, t, t, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        """Filled circle."""
        for dy in range(-r, r + 1):
            span = int(math.sqrt(max(0, r * r - dy * dy)))
            self.rect(cx - span, cy + dy, span * 2 + 1, 1, color)

    def ring(self, cx, cy, r, color, t=2):
        """Circle outline, t pixels thick."""
        for k in range(t):
            rr = r - k
            if rr <= 0:
                break
            for a in range(0, 360):
                rad = math.radians(a)
                self.px(cx + int(rr * math.cos(rad)),
                        cy + int(rr * math.sin(rad)), color)

    def star(self, cx, cy, r_out, r_in, color, rot=-90.0):
        """Five-pointed star as a filled polygon."""
        pts = []
        for k in range(10):
            r = r_out if k % 2 == 0 else r_in
            ang = math.radians(rot + k * 36.0)
            pts.append((cx + int(r * math.cos(ang)),
                        cy + int(r * math.sin(ang))))
        self.poly(pts, color)

    def poly(self, pts, color):
        """Filled polygon, even-odd scanline fill."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        x = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
                        xs.append(x)
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[k]))
                xb = int(math.floor(xs[k + 1]))
                if xb >= xa:
                    self.rect(xa, y, xb - xa + 1, 1, color)

    def save_png(self, path):
        """Write the framebuffer as an RGB PNG (filter 0, zlib level 9)."""
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * stride:(y + 1) * stride]
        comp = zlib.compress(bytes(raw), 9)

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        png = b"\x89PNG\r\n\x1a\n"
        png += chunk(b"IHDR", ihdr)
        png += chunk(b"IDAT", comp)
        png += chunk(b"IEND", b"")
        with open(path, "wb") as f:
            f.write(png)
        return len(png)


# ---------------------------------------------------------------- font
# Hand-written 5x7 bitmap font. Each glyph is 7 rows of 5 characters;
# "#" is ink, "." is empty. Uppercase A-Z, digits, and punctuation.

FONT = {
    "A": ("..#..",
          ".#.#.",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "B": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#...#",
          "#...#",
          "####."),
    "C": (".####",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          ".####"),
    "D": ("####.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "####."),
    "E": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#####"),
    "F": ("#####",
          "#....",
          "#....",
          "####.",
          "#....",
          "#....",
          "#...."),
    "G": (".####",
          "#....",
          "#....",
          "#.###",
          "#...#",
          "#...#",
          ".###."),
    "H": ("#...#",
          "#...#",
          "#...#",
          "#####",
          "#...#",
          "#...#",
          "#...#"),
    "I": (".###.",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "J": ("..###",
          "...#.",
          "...#.",
          "...#.",
          "...#.",
          "#..#.",
          ".##.."),
    "K": ("#...#",
          "#..#.",
          "#.#..",
          "##...",
          "#.#..",
          "#..#.",
          "#...#"),
    "L": ("#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#....",
          "#####"),
    "M": ("#...#",
          "##.##",
          "#.#.#",
          "#.#.#",
          "#...#",
          "#...#",
          "#...#"),
    "N": ("#...#",
          "##..#",
          "#.#.#",
          "#..##",
          "#...#",
          "#...#",
          "#...#"),
    "O": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "P": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#....",
          "#....",
          "#...."),
    "Q": (".###.",
          "#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "R": ("####.",
          "#...#",
          "#...#",
          "####.",
          "#.#..",
          "#..#.",
          "#...#"),
    "S": (".####",
          "#....",
          "#....",
          ".###.",
          "....#",
          "....#",
          "####."),
    "T": ("#####",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "U": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".###."),
    "V": ("#...#",
          "#...#",
          "#...#",
          "#...#",
          "#...#",
          ".#.#.",
          "..#.."),
    "W": ("#...#",
          "#...#",
          "#...#",
          "#.#.#",
          "#.#.#",
          "##.##",
          "#...#"),
    "X": ("#...#",
          ".#.#.",
          "..#..",
          "..#..",
          "..#..",
          ".#.#.",
          "#...#"),
    "Y": ("#...#",
          "#...#",
          ".#.#.",
          "..#..",
          "..#..",
          "..#..",
          "..#.."),
    "Z": ("#####",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#....",
          "#####"),
    "0": (".###.",
          "#...#",
          "#..##",
          "#.#.#",
          "##..#",
          "#...#",
          ".###."),
    "1": ("..#..",
          ".##..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".###."),
    "2": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          "#####"),
    "3": ("####.",
          "....#",
          "....#",
          ".###.",
          "....#",
          "....#",
          "####."),
    "4": ("...#.",
          "..##.",
          ".#.#.",
          "#..#.",
          "#####",
          "...#.",
          "...#."),
    "5": ("#####",
          "#....",
          "####.",
          "....#",
          "....#",
          "#...#",
          ".###."),
    "6": (".###.",
          "#....",
          "#....",
          "####.",
          "#...#",
          "#...#",
          ".###."),
    "7": ("#####",
          "....#",
          "...#.",
          "..#..",
          ".#...",
          ".#...",
          ".#..."),
    "8": (".###.",
          "#...#",
          "#...#",
          ".###.",
          "#...#",
          "#...#",
          ".###."),
    "9": (".###.",
          "#...#",
          "#...#",
          ".####",
          "....#",
          "....#",
          ".###."),
    " ": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "....."),
    ",": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "..#..",
          ".#..."),
    ".": (".....",
          ".....",
          ".....",
          ".....",
          ".....",
          ".....",
          "..#.."),
    "'": ("..#..",
          "..#..",
          ".....",
          ".....",
          ".....",
          ".....",
          "....."),
    "-": (".....",
          ".....",
          ".....",
          ".###.",
          ".....",
          ".....",
          "....."),
    ":": (".....",
          "..#..",
          ".....",
          ".....",
          ".....",
          "..#..",
          "....."),
    "/": ("....#",
          "...#.",
          "...#.",
          "..#..",
          ".#...",
          ".#...",
          "#...."),
    "(": ("...#.",
          "..#..",
          ".#...",
          ".#...",
          ".#...",
          "..#..",
          "...#."),
    ")": (".#...",
          "..#..",
          "...#.",
          "...#.",
          "...#.",
          "..#..",
          ".#..."),
    "!": ("..#..",
          "..#..",
          "..#..",
          "..#..",
          "..#..",
          ".....",
          "..#.."),
    "?": (".###.",
          "#...#",
          "....#",
          "...#.",
          "..#..",
          ".....",
          "..#.."),
    "&": (".##..",
          "#..#.",
          "#.#..",
          ".#...",
          "#.#.#",
          "#..#.",
          ".##.#"),
    "%": ("#...#",
          "#..#.",
          "...#.",
          "..#..",
          ".#...",
          "#..#.",
          "#...#"),
}


def text_width(text, scale):
    """Pixel width of text drawn with draw_text at this scale."""
    return len(text) * 6 * scale


def draw_text(cv, x, y, text, scale, color):
    """Draw one line of text; unknown glyphs render as blank."""
    cx = x
    for ch in text.upper():
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "#":
                    cv.rect(cx + col * scale, y + row * scale,
                            scale, scale, color)
        cx += 6 * scale
    return cx


def draw_text_centered(cv, cx, y, text, scale, color):
    draw_text(cv, cx - text_width(text, scale) // 2, y, text, scale, color)


def wrap_lines(text, max_width, scale):
    """Greedy word wrap; returns a list of lines fitting max_width."""
    words = text.split(" ")
    lines = []
    cur = ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, text, max_width, scale, color, leading=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    if leading is None:
        leading = 9 * scale
    for line in wrap_lines(text, max_width, scale):
        draw_text(cv, x, y, line, scale, color)
        y += leading
    return y


# ---------------------------------------------------------------- icons

def draw_flag_us(cv, x, y, w, h):
    for i in range(13):
        y0 = y + round(i * h / 13)
        y1 = y + round((i + 1) * h / 13)
        cv.rect(x, y0, w, y1 - y0, RED if i % 2 == 0 else WHITE)
    cw = int(w * 0.42)
    ch = round(7 * h / 13)
    cv.rect(x, y, cw, ch, NAVY)
    for r in range(4):
        for c in range(5):
            cv.disc(x + 5 + c * (cw - 10) // 4,
                    y + 5 + r * (ch - 10) // 3, 1, WHITE)


def draw_flag_cn(cv, x, y, w, h):
    cv.rect(x, y, w, h, RED)
    cv.star(x + int(w * 0.22), y + int(h * 0.28),
            max(6, h // 5), max(3, h // 12), YELLOW)
    for k in range(4):
        ang = math.radians(-30 + k * 28)
        sx = x + int(w * 0.22) + int(w * 0.34 * math.cos(ang))
        sy = y + int(h * 0.28) + int(h * 0.34 * math.sin(ang))
        cv.star(sx, sy, max(3, h // 12), max(1, h // 30), YELLOW)


def draw_flag_ru(cv, x, y, w, h):
    for i, band in enumerate((WHITE, SEA, RED)):
        y0 = y + round(i * h / 3)
        y1 = y + round((i + 1) * h / 3)
        cv.rect(x, y0, w, y1 - y0, band)


def draw_scales(cv, cx, cy, s, color):
    """Scales of justice, s = half-width in pixels."""
    cv.vline(cx, cy - s, 2 * s, color, 3)
    cv.hline(cx - s, cy - s, 2 * s, color, 3)
    cv.disc(cx, cy - s, 4, color)
    cv.rect(cx - 5, cy + s - 4, 10, 4, color)
    for side in (-1, 1):
        px = cx + side * s
        cv.line(px, cy - s, px - 14, cy - s + 26, color, 2)
        cv.line(px, cy - s, px + 14, cy - s + 26, color, 2)
        cv.poly([(px - 16, cy - s + 26), (px + 16, cy - s + 26),
                 (px, cy - s + 42)], color)


def draw_cyclone(cv, cx, cy, r, color):
    """Spiral storm: dots along an expanding coil, denser at the rim."""
    for deg in range(0, 720, 4):
        t = math.radians(deg)
        rad = r * deg / 720.0
        x = cx + int(rad * math.cos(t))
        y = cy + int(rad * 0.85 * math.sin(t))
        cv.disc(x, y, 3, color)
    cv.disc(cx, cy, 5, GOLD)
    cv.ring(cx, cy, r + 6, color, 2)


def draw_bridge(cv, x, y, w, h, color):
    """Suspension bridge with a blast starburst above its middle."""
    deck_y = y + int(h * 0.72)
    cv.hline(x, deck_y, w, color, 4)
    for tx in (x + int(w * 0.22), x + int(w * 0.72)):
        cv.rect(tx - 4, y + 10, 8, deck_y - y - 6, color)
        cv.rect(tx - 12, y + 4, 24, 8, color)
    cv.line(x + int(w * 0.22), y + 10, x + int(w * 0.5),
            deck_y, color, 2)
    cv.line(x + int(w * 0.72), y + 10, x + int(w * 0.5),
            deck_y, color, 2)
    cv.line(x, deck_y, x + int(w * 0.22), y + 10, color, 2)
    cv.line(x + w, deck_y, x + int(w * 0.72), y + 10, color, 2)
    cv.star(x + w // 2, y + int(h * 0.28), 26, 10, ORANGE)
    cv.star(x + w // 2, y + int(h * 0.28), 14, 5, YELLOW)
    cv.disc(x + w // 2 - 30, y + int(h * 0.14), 5, MUTED)
    cv.disc(x + w // 2 + 34, y + int(h * 0.10), 4, MUTED)


def draw_tanker(cv, x, y, w, h, color):
    """Oil tanker with a flame above it and waves below."""
    hull_y = y + int(h * 0.52)
    cv.poly([(x, hull_y), (x + w, hull_y),
             (x + int(w * 0.92), hull_y + 26), (x + int(w * 0.08),
                                                 hull_y + 26)], RED)
    cv.rect(x + int(w * 0.62), hull_y - 26, 30, 26, INK)
    cv.rect(x + int(w * 0.62) + 8, hull_y - 38, 14, 12, INK)
    cv.line(x + 4, hull_y - 34, x + int(w * 0.3), hull_y - 34, INK, 3)
    flame = [(x + int(w * 0.2), hull_y - 34),
             (x + int(w * 0.16), hull_y - 52),
             (x + int(w * 0.22), hull_y - 66),
             (x + int(w * 0.3), hull_y - 78),
             (x + int(w * 0.36), hull_y - 60),
             (x + int(w * 0.38), hull_y - 44)]
    cv.poly(flame, ORANGE)
    cv.poly([(x + int(w * 0.24), hull_y - 34),
             (x + int(w * 0.23), hull_y - 48),
             (x + int(w * 0.28), hull_y - 58),
             (x + int(w * 0.32), hull_y - 44)], YELLOW)
    for wy in (hull_y + 36, hull_y + 48):
        for k in range(6):
            wx = x + k * (w // 6)
            cv.line(wx, wy, wx + 12, wy - 5, SEA, 2)
            cv.line(wx + 12, wy - 5, wx + 24, wy, SEA, 2)


def draw_globe(cv, cx, cy, r, color):
    """Planet Earth: blue disc, green land blobs, orbit ring."""
    cv.disc(cx, cy, r, SKY)
    cv.ring(cx, cy, r, color, 3)
    cv.poly([(cx - r + 8, cy - 18), (cx - 6, cy - 34),
             (cx + 2, cy - 12), (cx - 14, cy + 2)], GREEN)
    cv.poly([(cx + 6, cy + 6), (cx + 26, cy - 4),
             (cx + 34, cy + 16), (cx + 12, cy + 26)], GREEN)
    cv.poly([(cx - 26, cy + 18), (cx - 8, cy + 14),
             (cx - 2, cy + 30), (cx - 22, cy + 34)], GREEN)
    cv.line(cx - r, cy, cx + r, cy, color, 1)
    cv.line(cx, cy - r, cx, cy + r, color, 1)


def draw_oil_drop(cv, cx, cy, s, color):
    """Oil drop with a red slash through it: fossil fuels dropped."""
    cv.disc(cx, cy + s // 3, s // 2, color)
    cv.poly([(cx - s // 2, cy + s // 3), (cx + s // 2, cy + s // 3),
             (cx, cy - s)], color)
    cv.line(cx - s, cy - s, cx + s, cy + s, RED, 5)


# ---------------------------------------------------------------- layout

def masthead(cv):
    cv.rect(0, 0, W, 148, NAVY)
    cv.rect(0, 148, W, 5, GOLD)
    draw_text_centered(cv, W // 2, 26, "THE WORLD TODAY", 7, WHITE)
    draw_text_centered(cv, W // 2, 96, "FRIDAY, 20 NOVEMBER 2026", 3, GOLD)
    draw_text_centered(cv, W // 2, 122, "ONE DAY IN THE WORLD - SUMMED UP IN A SINGLE IMAGE",
                       1, (200, 205, 220))


def lead_story(cv):
    x, y, w, h = 28, 168, 968, 262
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 3, GOLD)
    cv.rect(x, y + h - 3, w, 3, GOLD)
    tx = x + 24
    draw_text(cv, tx, y + 20, "LEAD STORY - BEIJING", 2, RED)
    draw_text(cv, tx, y + 52, "TRUMP, XI AND PUTIN", 5, INK)
    draw_text(cv, tx, y + 94, "MEET IN CHINA", 5, INK)
    draw_para(cv, tx, y + 152,
              "FIRST-EVER THREE-WAY SUMMIT PUTS NUCLEAR ARMS, ENERGY "
              "SECURITY AND THE WARS IN UKRAINE AND THE GULF ON THE TABLE.",
              596, 2, INK)
    fx = x + 648
    draw_flag_us(cv, fx, y + 44, 96, 62)
    draw_flag_cn(cv, fx + 108, y + 44, 96, 62)
    draw_flag_ru(cv, fx + 216, y + 44, 96, 62)
    for fxx in (fx, fx + 108, fx + 216):
        cv.hline(fxx, y + 44, 96, INK, 1)
        cv.hline(fxx, y + 44 + 61, 96, INK, 1)
        cv.vline(fxx, y + 44, 62, INK, 1)
        cv.vline(fxx + 95, y + 44, 62, INK, 1)
    draw_text_centered(cv, fx + 48, y + 114, "USA", 2, INK)
    draw_text_centered(cv, fx + 156, y + 114, "CHINA", 2, INK)
    draw_text_centered(cv, fx + 264, y + 114, "RUSSIA", 2, INK)
    cv.hline(fx, y + 150, 312, GREY_LINE, 2)
    draw_text(cv, fx, y + 166, "THREE LEADERS, ONE TABLE:", 2, MUTED)
    draw_para(cv, fx, y + 190,
              "TALKS IN CHINA OPEN WITH A JOINT CALL TO LOWER NUCLEAR "
              "RISKS.", 312, 2, INK)


def story_cell(cv, x, y, w, h, icon, headline, sub):
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 2, NAVY)
    icon(x + 16, y + 20, 118, 118)
    tx = x + 150
    tw = w - 150 - 18
    yy = y + 18
    for line in wrap_lines(headline, tw, 3):
        draw_text(cv, tx, yy, line, 3, INK)
        yy += 27
    yy += 4
    draw_para(cv, tx, yy, sub, tw, 2, MUTED)


def bottom_story(cv):
    x, y, w, h = 28, 808, 968, 160
    cv.rect(x, y, w, h, CARD)
    cv.rect(x, y, w, 2, TEAL)
    draw_globe(cv, x + 92, y + 80, 56, NAVY)
    draw_oil_drop(cv, x + 172, y + 80, 34, INK)
    tx = x + 224
    draw_text(cv, tx, y + 26, "COP31 DRAFT DROPS", 4, INK)
    draw_text(cv, tx, y + 62, "FOSSIL FUELS", 4, INK)
    draw_para(cv, tx, y + 106,
              "CLIMATE TALKS IN TURKIYE CUT THE REFERENCE TO ENDING "
              "FOSSIL FUELS FROM THE DRAFT DEAL.", 700, 2, MUTED)


def footer(cv):
    draw_text_centered(cv, W // 2, 992,
                       "REPORTS PUBLISHED FRIDAY 20 NOVEMBER 2026 - DRAWN "
                       "ENTIRELY IN CODE, NO PHOTOGRAPHS", 1, MUTED)


def build():
    cv = Canvas(W, H, PAPER)
    masthead(cv)
    lead_story(cv)
    cells = [
        (28, 448, lambda a, b, c, d: draw_scales(cv, a + 59, b + 52, 42, NAVY),
         "MYANMAR GUILTY OF GENOCIDE",
         "WORLD COURT RULES THE 2017 CRACKDOWN ON THE ROHINGYA WAS "
         "GENOCIDE. NO APPEAL."),
        (524, 448, lambda a, b, c, d: draw_cyclone(cv, a + 59, b + 59, 42, TEAL),
         "CYCLONE AKVAN MAKES LANDFALL",
         "STORM CROSSES INDIA'S EAST COAST AS 80,000 FLEE ODISHA AND "
         "ANDHRA PRADESH."),
        (28, 628, lambda a, b, c, d: draw_bridge(cv, a + 6, b + 14, 108, 96, NAVY),
         "UKRAINE HITS CRIMEAN BRIDGE",
         "THIRD STRIKE ON THE BRIDGE THIS WEEK. RUSSIAN BLASTS DAMAGE "
         "EMBASSIES IN KYIV."),
        (524, 628, lambda a, b, c, d: draw_tanker(cv, a + 6, b + 14, 108, 96, NAVY),
         "IRAN WIDENS GULF ATTACKS",
         "TANKERS AND GULF STATES HIT. ENERGY WATCHDOG CALLS IT A "
         "HISTORIC THREAT."),
    ]
    for (cx, cy, icon, head, sub) in cells:
        story_cell(cv, cx, cy, 472, 160, icon, head, sub)
    bottom_story(cv)
    footer(cv)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = build().save_png(path)
    print("wrote %s (%d bytes)" % (path, size))


if __name__ == "__main__":
    main()
