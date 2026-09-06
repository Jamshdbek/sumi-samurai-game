"""Minimal PNG read/write (8-bit RGBA, non-interlaced) plus a box downsampler.
No image library is available on this machine, so the asset pipeline needs its
own. Shared by the sprite-packing scripts."""
import struct, zlib

def read_png(path):
    d = open(path, 'rb').read()
    assert d[:8] == b'\x89PNG\r\n\x1a\n', path
    pos, idat, pal, trns = 8, [], None, None
    w = h = ct = bd = None
    while pos < len(d):
        ln = struct.unpack('>I', d[pos:pos+4])[0]
        typ = d[pos+4:pos+8]; body = d[pos+8:pos+8+ln]
        if typ == b'IHDR':
            w, h, bd, ct, _, _, il = struct.unpack('>IIBBBBB', body)
            assert bd == 8 and il == 0, f'{path}: bd{bd} il{il}'
        elif typ == b'PLTE': pal = body
        elif typ == b'tRNS': trns = body
        elif typ == b'IDAT': idat.append(body)
        elif typ == b'IEND': break
        pos += 12 + ln
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    raw = zlib.decompress(b''.join(idat))
    stride = w * ch
    rows, prev, p = [], bytearray(stride), 0
    for _ in range(h):
        f = raw[p]; p += 1
        line = bytearray(raw[p:p+stride]); p += stride
        if f == 1:
            for i in range(ch, stride): line[i] = (line[i] + line[i-ch]) & 255
        elif f == 2:
            for i in range(stride): line[i] = (line[i] + prev[i]) & 255
        elif f == 3:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                line[i] = (line[i] + ((a + prev[i]) >> 1)) & 255
        elif f == 4:
            for i in range(stride):
                a = line[i-ch] if i >= ch else 0
                b = prev[i]; c = prev[i-ch] if i >= ch else 0
                pa, pb, pc = abs(b-c), abs(a-c), abs(a+b-2*c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[i] = (line[i] + pr) & 255
        elif f != 0: raise ValueError(f'{path}: filter {f}')
        rows.append(line); prev = line
    # normalise everything to RGBA
    out = bytearray(w * h * 4)
    for y, line in enumerate(rows):
        for x in range(w):
            o = (y*w + x) * 4
            if ct == 6:   px = line[x*4:x*4+4]
            elif ct == 2: px = bytes(line[x*3:x*3+3]) + b'\xff'
            elif ct == 4: px = bytes([line[x*2]]*3) + bytes([line[x*2+1]])
            elif ct == 0: px = bytes([line[x]]*3) + b'\xff'
            else:
                i = line[x]; px = pal[i*3:i*3+3] + bytes([trns[i] if trns and i < len(trns) else 255])
            out[o:o+4] = px
    return w, h, out

def write_png(path, w, h, px):
    raw = bytearray(); stride = w * 4
    for y in range(h):
        raw.append(0); raw += px[y*stride:(y+1)*stride]
    def chunk(t, b):
        return struct.pack('>I', len(b)) + t + b + struct.pack('>I', zlib.crc32(t+b) & 0xffffffff)
    open(path, 'wb').write(
        b'\x89PNG\r\n\x1a\n'
        + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
        + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
        + chunk(b'IEND', b''))

def blit(dst, dw, src, sw, sh, ox, oy):
    for y in range(sh):
        d = ((oy+y)*dw + ox) * 4
        s = (y*sw) * 4
        dst[d:d+sw*4] = src[s:s+sw*4]
