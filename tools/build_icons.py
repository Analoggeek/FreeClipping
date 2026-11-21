#!/usr/bin/env python3
"""Build FreeClipping's 3D icon set from the master tile crop.

Reads   icons/master.png   (the tile crop — the 3D glossy bolt)
writes  icons/app-icon-*.png, icons/app-icon-maskable-512.png,
        icons/app-icon.ico, icons/app-icon.icns, icons/favicon-*.png

All steps run offline after the master is generated with an image model.
"""
import struct
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / 'icons'
TILE = ICONS / 'master.png'

# hex of the dark indigo mask background (edge-ish of the tile)
BG = (15, 12, 32)

def resize_png(src, size):
    img = Image.open(src).convert('RGBA')
    img = img.resize((size, size), Image.LANCZOS)
    return img

def crop_tile():
    master = Image.open(ICONS / 'master-3d.png').convert('RGB')
    # new master-3d.png (2048x2048): tile spans x:407..1622, y:410..1622 (rounded-square just-detected)
    crop = master.crop((407, 410, 1622, 1622))
    crop.save(TILE)
    return TILE

def maskable(tile_src, size=512):
    """Full-bleed dark background + tile scaled to the safe zone."""
    canvas = Image.new('RGBA', (size, size), BG + (255,))
    inner = resize_png(tile_src, int(size * 0.86))
    off = (size - inner.size[0]) // 2
    canvas.paste(inner, (off, off))
    return canvas

def build_ico(tile_src, out, sizes=(16, 24, 32, 48, 64, 128, 256, 512)):
    img = resize_png(tile_src, 512)
    img.save(out, format='ICO', sizes=[(s, s) for s in sizes])

def build_icns(tile_src, out):
    """Minimal .icns (PNG payloads): 16/32/128/256/512/1024."""
    # build one 1024 canvas and downscale for each entry
    big = resize_png(tile_src, 1024)
    entries = []
    for code, size in [(b'ic04', 16), (b'ic05', 32), (b'ic07', 128), (b'ic08', 256), (b'ic09', 512), (b'ic10', 1024)]:
        if size == 1024:
            png_img = big
        else:
            png_img = resize_png(tile_src, size)
        buf = BytesIO()
        png_img.save(buf, format='PNG')
        entries.append((code, buf.getvalue()))
    total = 8
    for code, data in entries:
        total += 8 + len(data)
    with open(out, 'wb') as f:
        f.write(b'icns')
        f.write(struct.pack('>I', total))
        for code, data in entries:
            f.write(code)
            f.write(struct.pack('>I', 8 + len(data)))
            f.write(data)

def main():
    if not (ICONS / 'master-3d.png').exists():
        print('master-3d.png missing - generate the master first', file=sys.stderr)
        sys.exit(1)
    tile = crop_tile()
    # core sizes (RGBA, clean edges)
    for n, s in [('app-icon-1024', 1024), ('app-icon-512', 512), ('app-icon-192', 192),
                 ('app-icon-180', 180), ('app-icon-32', 32), ('app-icon-16', 16)]:
        resize_png(tile, s).save(ICONS / f'{n}.png')
    mask = maskable(tile, 512)
    mask.save(ICONS / 'app-icon-maskable-512.png')
    build_ico(tile, ICONS / 'app-icon.ico')
    build_icns(tile, ICONS / 'app-icon.icns')
    sizes = {'master': Image.open(ICONS / 'master-3d.png').size[0]}
    print('icons built:')
    for p in sorted(ICONS.iterdir()):
        print(f'  {p.name:38s} {p.stat().st_size:>9} bytes')

if __name__ == '__main__':
    main()
