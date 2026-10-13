# Billboard source files

The 18 billboards are drawn in code. `make_boards_v3.py` runs `make_boards_v2.py` and then redraws 7 boards.

    python3 make_boards_v3.py <output_folder>

That writes `<id>.svg` for all 18 boards (hf, fmd, bp, chol, cpr, stroke × A, B, C) plus `options.json`.
The web address on every board is set by `SITE_URL` in `make_boards_v2.py`.

To make the JPG previews and full-size files, serve the output folder on port 4175 with `render.html` and
`render-full.html` inside it, then use headless Chrome (see `render_all.sh`). The finished files used by the
website are in `assets/billboards/`.
