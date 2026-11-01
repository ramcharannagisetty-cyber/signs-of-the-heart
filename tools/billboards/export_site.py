"""Copy finished formats into the website folder: full-size JPG (quality 80), SVG and a small thumbnail.
usage: python3 -I export_site.py <render_out_dir> <site_formats_dir>"""
import json, os, shutil, sys
from PIL import Image

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
files = json.load(open(os.path.join(src, "svg", "formats.json")))["files"]
for f in files:
    n = f["file"][:-4]
    im = Image.open(os.path.join(src, "png", n + ".png")).convert("RGB")
    im.save(os.path.join(dst, n + ".jpg"), quality=80, optimize=True, progressive=True)
    th = im.copy()
    th.thumbnail((480, 480), Image.LANCZOS)
    th.save(os.path.join(dst, n + "-thumb.jpg"), quality=78, optimize=True, progressive=True)
    shutil.copy(os.path.join(src, "svg", n + ".svg"), os.path.join(dst, n + ".svg"))
print(len(files), "formats exported")
