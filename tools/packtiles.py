"""Pack the dark tileset into one 12x8 atlas of 32px cells, and grade it.

The source ships 96 separate files, which the loader would rather see as one
sheet. It also ships a magenta-maroon stone that is nowhere in this game's
palette; the sheet is only ten colours, so the grade below is an explicit
remap rather than a filter. The greens survive (a ledge has to be readable at
a glance); the magenta goes to the same ink the rest of the world is drawn in.
"""
import glob, os, re
from pnglib import read_png, write_png

SRC = '/Users/o/Documents/my-games/dark-platform/1 Tiles'
DST = '/Users/o/Documents/my-games/sumi-samurai-game/public/assets/world/tiles_dark.png'
COLS, TILE = 12, 32

GRADE = {
    (0x38, 0x00, 0x2c): (0x16, 0x14, 0x22),   # the magenta wall -> ink
    (0x32, 0x19, 0x33): (0x21, 0x1e, 0x33),   # its highlight
    (0x22, 0x2a, 0x5c): (0x2d, 0x2c, 0x48),   # brick, already indigo
    (0x2c, 0x5b, 0x6d): (0x30, 0x4c, 0x64),
    (0x15, 0x89, 0x68): (0x1e, 0x7b, 0x62),
    (0x56, 0x6a, 0x89): (0x56, 0x66, 0x8a),
    (0x46, 0xc6, 0x57): (0x59, 0xb8, 0x5a),   # grass, a shade off neon
    (0xc9, 0xec, 0x85): (0xbc, 0xdd, 0x7e),
    (0x8b, 0xab, 0xbf): (0x8a, 0xa6, 0xbc),
}

files = sorted(glob.glob(f'{SRC}/Tile_*.png'),
               key=lambda p: int(re.search(r'(\d+)', os.path.basename(p)).group(1)))
rows = (len(files) + COLS - 1) // COLS
W, H = COLS * TILE, rows * TILE
out = bytearray(W * H * 4)
for i, p in enumerate(files):
    w, h, px = read_png(p)
    ox, oy = (i % COLS) * TILE, (i // COLS) * TILE
    for y in range(min(h, TILE)):
        for x in range(min(w, TILE)):
            s = (y * w + x) * 4
            if px[s+3] == 0:
                continue
            rgb = GRADE.get((px[s], px[s+1], px[s+2]))
            o = ((oy + y) * W + ox + x) * 4
            if rgb:
                out[o:o+3] = bytes(rgb)
            else:
                out[o:o+3] = px[s:s+3]
            out[o+3] = px[s+3]
write_png(DST, W, H, bytes(out))
print(f'packed {len(files)} tiles -> {W}x{H}, {os.path.getsize(DST)} bytes')
