# Asset pipeline

The art in `public/assets` is packed from the CraftPix source packs that live
next to this repo in `../`. Nothing here runs at build time — the sheets are
committed — but these are the scripts that produced them, so a sheet can be
regenerated after a source pack is updated or a colour grade is retuned.

There is no image library on the machine this was built on, so `pnglib.py` is a
minimal PNG reader/writer (8-bit, non-interlaced) that the rest share.

| script | reads | writes |
| --- | --- | --- |
| `packboss.py` | `../free-bosses/{1,2,3}*/` | `public/assets/boss/{mech,ooze,bear}.png` |
| `packtiles.py` | `../dark-platform/1 Tiles/` | `public/assets/world/tiles_dark.png` |
| `packbg.py` | `../dark-platform/2 Background/Night/` | `public/assets/bg/night_*.png` |

Run them from this directory: `python3 tools/packboss.py`.
