"""Pack the three boss characters into one 96px-cell strip each.

The source pack ships each boss as twelve separate 90x90 expression stills, no
animation. The game's sprite pipeline reads horizontal strips of 96px cells, so
each boss becomes one strip and the states below index into it by frame.
"""
import os
from pnglib import read_png, write_png

SRC = '/Users/o/Documents/my-games/free-bosses'
DST = '/Users/o/Documents/my-games/sumi-samurai-game/public/assets/boss'
CELL = 96

# Frame order is the state machine's order, not the pack's alphabetical one.
ORDER = ['Calm', 'Thoughtful', 'Talking', 'Amazed', 'Mocking', 'Irritated',
         'Angry', 'Furious', 'Scared', 'Stunning', 'Upset', 'Sad']
BOSSES = [('1 Ancient_mech', 'mech'), ('2 Frost_ooze', 'ooze'), ('3 Magic_bear', 'bear')]

def bbox(w, h, px):
    x0, y0, x1, y1 = w, h, -1, -1
    for y in range(h):
        for x in range(w):
            if px[(y*w+x)*4+3] > 8:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    return x0, y0, x1, y1

os.makedirs(DST, exist_ok=True)
for folder, name in BOSSES:
    frames = []
    for e in ORDER:
        w, h, px = read_png(f'{SRC}/{folder}/{e}.png')
        frames.append((w, h, px))
    # One shared bbox across the whole set, so the boss does not jitter when the
    # expression changes mid-fight.
    b = [CELL, CELL, -1, -1]
    for w, h, px in frames:
        x0, y0, x1, y1 = bbox(w, h, px)
        b = [min(b[0], x0), min(b[1], y0), max(b[2], x1), max(b[3], y1)]
    bw, bh = b[2]-b[0]+1, b[3]-b[1]+1
    ox = (CELL - bw)//2 - b[0]
    oy = (CELL - bh)//2 - b[1]
    W = CELL*len(frames)
    out = bytearray(W*CELL*4)
    for i, (w, h, px) in enumerate(frames):
        for y in range(h):
            ty = y+oy
            if not (0 <= ty < CELL): continue
            for x in range(w):
                tx = i*CELL + x + ox
                if not (i*CELL <= tx < (i+1)*CELL): continue
                s = (y*w+x)*4
                if px[s+3] == 0: continue
                o = (ty*W+tx)*4
                out[o:o+4] = px[s:s+4]
    write_png(f'{DST}/{name}.png', W, CELL, bytes(out))
    print(f'{name}: bbox {bw}x{bh} -> {W}x{CELL}, {os.path.getsize(f"{DST}/{name}.png")} bytes')
