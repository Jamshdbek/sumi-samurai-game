"""Pack the night parallax plates for the dark theme.

The source pack is a modern city park at night; only two of its five plates
belong in a samurai game (the sky gradient and the tree silhouettes), and both
ship in a neutral grey that fights the game's indigo. Both are recoloured here
onto the palette the rest of the world is painted in.
"""
import os
from pnglib import read_png, write_png

SRC = '/Users/o/Documents/my-games/dark-platform/2 Background/Night'
DST = '/Users/o/Documents/my-games/sumi-samurai-game/public/assets/bg'

def lerp(a, b, t): return int(a + (b - a) * t + 0.5)

# ---- sky: grey vertical ramp -> the game's indigo, opaque -------------------
w, h, px = read_png(f'{SRC}/1.png')
TOP, BOT = (0x17, 0x15, 0x28), (0x3C, 0x37, 0x56)
out = bytearray(w * h * 4)
for y in range(h):
    for x in range(w):
        s = (y * w + x) * 4
        # luminance of the source drives the ramp, so its dither survives
        l = (px[s] * 299 + px[s+1] * 587 + px[s+2] * 114) // 1000
        t = min(1.0, max(0.0, (l - 0x50) / 0x40))
        o = s
        out[o] = lerp(TOP[0], BOT[0], t)
        out[o+1] = lerp(TOP[1], BOT[1], t)
        out[o+2] = lerp(TOP[2], BOT[2], t)
        out[o+3] = 255
write_png(f'{DST}/night_sky.png', w, h, bytes(out))
print('night_sky', w, h, os.path.getsize(f'{DST}/night_sky.png'))

# ---- trees: silhouette flattened to one ink value, alpha kept --------------
w, h, px = read_png(f'{SRC}/5.png')
INK = (0x1B, 0x19, 0x2E)
opaque = sum(1 for i in range(w * h) if px[i*4+3] > 0)
out = bytearray(w * h * 4)
mir = bytearray(w * h * 4)
for y in range(h):
    for x in range(w):
        s = (y * w + x) * 4
        a = px[s+3]
        o = s
        out[o:o+3] = bytes(INK); out[o+3] = a
        m = (y * w + (w - 1 - x)) * 4
        mir[m:m+3] = bytes(INK); mir[m+3] = a
write_png(f'{DST}/night_trees.png', w, h, bytes(out))
write_png(f'{DST}/night_trees2.png', w, h, bytes(mir))
print('night_trees', w, h, 'opaque px', opaque, os.path.getsize(f'{DST}/night_trees.png'))
