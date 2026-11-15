"""Add a fieldwork trip to the gallery from a folder of exported photos.

    python3 add_trip.py "Place name" YEAR /path/to/photos [--kind "Field trip"]

Photos are resized to 1400 px on the long side, saved as WebP in assets/fieldwork/<slug>/ with all metadata
(GPS included) removed, and listed in data/misc.json in file order. Tile shapes are picked from each photo's
orientation. Then add the pin to FIELD_SITES and the text to FIELD_TEXT in build.py and run build.py.
Every trip gallery is drawn as a packed collage (see collage_layout in build.py). Do not use grids or columns.
"""
import json, os, re, sys, unicodedata
from PIL import Image, ImageOps

args = sys.argv[1:]
kind = "Fieldwork"
if "--kind" in args:
    i = args.index("--kind"); kind = args[i + 1]; del args[i:i + 2]
place, src = args[0], args[2]
year = int(args[1]) if args[1].isdigit() else args[1]  # e.g. "2023 and 2025"
slug = re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", place).encode("ascii", "ignore").decode().lower()).strip("-")
dst = f"assets/fieldwork/{slug}"
os.makedirs(dst, exist_ok=True)
num = lambda f: int(m.group(1)) if (m := re.search(r"(\d+) of \d+", f)) else 0
files = sorted([f for f in os.listdir(src) if f.lower().endswith((".jpg", ".jpeg", ".png", ".heic", ".webp"))], key=lambda f: (num(f), f))
P, L = ["3/4", "2/3", "4/5", "1/1"], ["4/3", "3/2", "16/10"]
photos, ratios, ip, il = [], [], 0, 0
for k, f in enumerate(files, 1):
    im = ImageOps.exif_transpose(Image.open(os.path.join(src, f))).convert("RGB")
    im.thumbnail((1400, 1400), Image.LANCZOS)
    name = f"{dst}/{slug}-{k:02d}.webp"
    im.save(name, "WEBP", quality=72, method=6)
    photos.append(name)
    if im.height > im.width: ratios.append(P[ip % 4]); ip += 1
    else: ratios.append(L[il % 3]); il += 1
d = json.load(open("data/misc.json"))
d["fieldwork"] = [t for t in d["fieldwork"] if t["place"] != place]
d["fieldwork"].append({"place": place, "year": year, "kind": kind, "photos": photos, "ratios": ratios})
json.dump(d, open("data/misc.json", "w"), ensure_ascii=False, indent=1)
open("data/misc.json", "a").write("\n")
print(f"{len(photos)} photos added for {place}. Now add FIELD_SITES and FIELD_TEXT entries in build.py.")
