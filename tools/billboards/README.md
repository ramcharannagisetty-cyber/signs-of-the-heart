# Billboard source files

The 18 billboards are drawn in code. `make_boards_v3.py` runs `make_boards_v2.py` and then redraws 7 boards.

    python3 make_boards_v3.py <output_folder>

That writes `<id>.svg` for all 18 boards (hf, fmd, bp, chol, cpr, stroke × A, B, C) plus `options.json`.
The web address on every board is set by `SITE_URL` in `make_boards_v2.py`.

To make the JPG previews and full-size files, serve the output folder on port 4175 with `render.html` and
`render-full.html` inside it, then use headless Chrome (see `render_all.sh`). The finished files used by the
website are in `assets/billboards/`.

## Other shapes (square, portrait, story, widescreen)

Every board also comes in four more shapes: square 1:1, portrait 4:5, story 9:16 and widescreen 16:9. Each one is
laid out again for its shape (text re-sized and re-wrapped, art moved), not cropped. `make_formats.py` builds them from
the same art as the billboards.

    ./run_formats.sh <output_folder>                       # builds the SVGs and renders PNG/JPG (needs Chrome)
    python3 export_site.py <output_folder> ../../assets/billboards/formats   # copies JPG, SVG and thumbnails into the site

`text-widths.json` caches text widths measured from the real fonts (run_formats.sh measures any new text itself).
`art-boxes.json` holds the bounding box of each piece of art; rebuild it with `python3 make_formats.py <dir> --probe`
if the art changes. The download popup on billboards.html lists the shapes from `billboards.formats` in `assets/data.base.js`.
