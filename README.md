# Two Way Miss Studio website

Live site: https://twowaymissstudio-rgb.github.io/twm-website/

## Editing the site

1. Open `editor.html` from this folder in **Chrome** (or Edge). Safari can't save into folders.
2. Click **Open site folder**, choose this `twm-website` folder, and click **Allow**.
3. Edit listings, add, remove or reorder photos, or create a new listing. Click **Save changes** (or press Cmd+S).
4. In GitHub Desktop, write a short summary, click **Commit to main**, then click **Push origin**.

GitHub rebuilds the site and publishes it about a minute after you push. You can watch progress in the repository's **Actions** tab.

## How it fits together

- `listings.json` holds every listing (title, category, location, details, description, photos) plus the home page photos. The editor reads and writes this file.
- `build.py` turns `listings.json` into `index.html`, one page per listing in `listing/<name>/`, `sitemap.xml` and `robots.txt`. GitHub runs it on every push (see `.github/workflows/deploy.yml`), so you don't need to run it yourself.
- `style.css` and `site.js` are shared by every page.
- Photos: `img/` holds the large versions (about 1600px) and `img/t/` the thumbnails (about 800px). The editor makes both sizes when you add a photo.
- `editor.html`, `build.py` and this README are not published. Only the site itself goes live.

Categories: `ace` (hole-in-one), `hole` (signature holes), `course` (course maps), `city` (city & coast).

Don't edit `index.html` or the `listing/` pages by hand. They're rebuilt every time the site is published.
