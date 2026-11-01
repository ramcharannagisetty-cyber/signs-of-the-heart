#!/bin/zsh
# Build every board in every shape, then render JPGs.
# usage: run_formats.sh <out_dir>   (serves this folder on port 4176 while it runs)
set -e
HERE="${0:A:h}"; OUT="${1:A}"; CH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROF="$(mktemp -d)"
cd "$HERE"
python3 -m http.server 4176 --bind 127.0.0.1 >/dev/null 2>&1 & SRV=$!
trap 'kill $SRV 2>/dev/null' EXIT
sleep 1
measure() {
  "$CH" --headless=new --disable-gpu --user-data-dir="$PROF/m" --virtual-time-budget=15000 --dump-dom "http://127.0.0.1:4176/measure.html" 2>/dev/null \
    | python3 -I -c 'import sys,re,json,html; s=sys.stdin.read(); m=re.search(r"<pre id=\"out\">(.*?)</pre>",s,re.S); d=json.loads(html.unescape(m.group(1))); p=sys.argv[1]; import os; old=json.load(open(p)) if os.path.exists(p) else {}; old.update(d); json.dump(old,open(p,"w"),ensure_ascii=False); print(len(d),"widths measured")' "$HERE/text-widths.json"
}
for i in 1 2 3 4 5 6 7 8 9 10; do
  if python3 -I make_formats.py "$OUT/svg"; then break; fi
  measure
done
mkdir -p "$OUT/png" "$OUT/jpg"
python3 -I -c 'import json,sys; [print(f["file"][:-4], f["width"], f["height"]) for f in json.load(open(sys.argv[1]))["files"]]' "$OUT/svg/formats.json" > "$OUT/list.txt"
render() {
  local n=$1 w=$2 h=$3 slot=$4
  ln -sf "$OUT/svg/$n.svg" "$HERE/_r_$n.svg"
  "$CH" --headless=new --disable-gpu --hide-scrollbars --user-data-dir="$PROF/r$slot" --window-size=$w,$h \
    --virtual-time-budget=12000 --screenshot="$OUT/png/$n.png" "http://127.0.0.1:4176/render-formats.html?f=_r_$n.svg" >/dev/null 2>&1
  rm -f "$HERE/_r_$n.svg"
  python3 -I -c 'import sys; from PIL import Image; Image.open(sys.argv[1]).convert("RGB").save(sys.argv[2], quality=80, optimize=True, progressive=True)' "$OUT/png/$n.png" "$OUT/jpg/$n.jpg"
}
k=0; pids=()
while read n w h; do
  render $n $w $h $((k % 6)) & pids+=($!)
  k=$((k+1)); if (( k % 6 == 0 )); then wait $pids; pids=(); fi
done < "$OUT/list.txt"
(( ${#pids} )) && wait $pids
ls "$OUT/jpg" | wc -l
