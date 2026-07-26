# skyler-hughes-photography

Static photography portfolio site for Skyler Hughes, deployed via GitHub Pages at
https://skylerhughes.github.io/skyler-hughes-photography/

## Structure

- `js/data.js` — single source of truth for all site content: nav/gallery labels,
  every photo (file, alt text, dimensions), and the About bio. Edit this to add,
  remove, or reorder photos and galleries.
- `build_site.py` — generates the static HTML from `js/data.js`: `index.html`,
  one directory per gallery (`central-oregon/`, `pacific-northwest/`, etc.) and
  `about/`, each with its own `index.html`, plus `sitemap.xml` and `robots.txt`.
  Each generated page has real server-rendered content (photos, headings, bio
  text, JSON-LD structured data) so it reads correctly without JavaScript.
- `js/app.js` — enhances the server-rendered photo grid into a justified-row
  layout and powers the lightbox and mobile nav toggle.
- `css/style.css` — all styling.
- `images/` — photo assets, referenced by filename from `js/data.js`.

## Making changes

1. Edit `js/data.js` (add a photo, change the bio, add a gallery, etc.).
2. Regenerate the static pages:
   ```
   python3 build_site.py
   ```
3. Preview locally:
   ```
   python3 -m http.server 8000
   ```
   then open http://localhost:8000/ — don't open the files directly via `file://`,
   since directory-style URLs (e.g. `/about/`) need a real server to resolve to
   `index.html`.
4. Commit both `js/data.js` and the regenerated output (`index.html`, the
   gallery/about directories, `sitemap.xml`, `robots.txt`).
