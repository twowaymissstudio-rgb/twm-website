# Two Way Miss Studio website

Live site: https://twowaymissstudio-rgb.github.io/twm-website/

## How it's built

- `listings.json` is the list of every piece on the site: title, category, location, specs, description and photos.
- `build.py` reads it and writes `index.html`, one page per listing in `listing/<name>/`, plus `sitemap.xml` and `robots.txt`.
- `style.css` and `site.js` are shared by every page.
- Photos: `img/` holds the large versions (about 1600px) and `img/t/` the thumbnails (about 800px).

## Adding a listing

1. Put the large photos in `img/`.
2. Add an entry to `listings.json`. The first photo is the cover, and the second is the one shown when someone hovers over the card.
3. Run `python3 build.py` from this folder.
4. Commit and push in GitHub Desktop.

Categories: `ace` (hole-in-one), `hole` (signature holes), `course` (course maps), `city` (city & coast).
Add `"etsy": "https://www.etsy.com/listing/..."` to a listing to link its button straight to that Etsy listing.

Don't edit `index.html` or the `listing/` pages by hand. They're rebuilt every time `build.py` runs.
