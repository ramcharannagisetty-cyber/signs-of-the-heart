#!/bin/zsh
# usage: render_all.sh <out_dir> <scratch> [ids...]
OUT="$1"; S="$2"; shift 2
CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
mkdir -p "$OUT/renders"
ids=("$@"); [ ${#ids} -eq 0 ] && ids=(${(f)"$(cd "$OUT" && ls *.svg | sed 's/\.svg$//')"})
for id in $ids; do
  "$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$S/chrome-render" --window-size=1600,467 \
    --virtual-time-budget=12000 --screenshot="$OUT/renders/$id.png" "http://127.0.0.1:4175/render.html?f=$id.svg" >/dev/null 2>&1
done
ls "$OUT/renders" | wc -l
