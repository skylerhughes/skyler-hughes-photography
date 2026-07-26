#!/usr/bin/env python3
"""Generates the static HTML pages (index.html, /central-oregon/index.html, ...)
from js/data.js. Re-run this after editing js/data.js (new photos, new gallery,
changed bio, etc.) to keep every page's nav/meta in sync.
"""

import json
import os

BASE = os.path.dirname(os.path.abspath(__file__))
SITE_BASE_URL = "https://skylerhughes.github.io/skyler-hughes-photography/"


def load_data():
    raw = open(os.path.join(BASE, "js/data.js")).read()
    raw = raw[raw.index("{"):].rstrip().rstrip(";")
    return json.loads(raw)


def page_list(data):
    pages = [{"id": "home", "label": "Home", "slug": ""}]
    for item in data["nav"]:
        pages.append({"id": item["id"], "label": item["label"], "slug": item["id"] + "/"})
    pages.append({"id": "about", "label": "About", "slug": "about/"})
    return pages


def html_escape(s):
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_nav(data, pages, active_id, depth):
    prefix = "../" if depth else ""
    gallery_ids = {item["id"] for item in data["nav"]}

    gallery_lis = []
    for item in data["nav"]:
        active = " active" if item["id"] == active_id else ""
        href = prefix if item["id"] == "home" else prefix + item["id"] + "/"
        gallery_lis.append(
            '<li><a href="{href}" class="{cls}">{label}</a></li>'.format(
                href=href, cls=("nav-link" + active).strip(), label=html_escape(item["label"])
            )
        )

    about_active = " active" if active_id == "about" else ""

    return """
<a href="{home_href}" class="site-name">Skyler<br>Hughes</a>

    <nav class="site-nav" aria-label="Primary">
      <div class="nav-group">
        <span class="nav-group-label">Image Galleries</span>
        <ul>
          {gallery_lis}
        </ul>
      </div>
      <ul class="nav-flat">
        <li><a href="{about_href}" class="nav-link{about_active}">About</a></li>
      </ul>
    </nav>""".format(
        home_href=prefix if prefix else "./",
        gallery_lis="\n          ".join(gallery_lis),
        about_href=prefix + "about/",
        about_active=about_active,
    )


def render_head(title, description, canonical_slug, og_image_path, depth):
    asset_prefix = "../" if depth else ""
    canonical_url = SITE_BASE_URL + canonical_slug
    og_image_url = SITE_BASE_URL + og_image_path
    return """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical_url}">

<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:image" content="{og_image_url}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image_url}">

<link rel="stylesheet" href="{asset_prefix}css/style.css">""".format(
        title=html_escape(title),
        description=html_escape(description),
        canonical_url=canonical_url,
        og_image_url=og_image_url,
        asset_prefix=asset_prefix,
    )


PAGE_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
{head}
</head>
<body>

<button id="nav-toggle" class="nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
  <span></span><span></span><span></span>
</button>

<aside class="sidebar" id="sidebar">
  <div class="sidebar-inner">
    {nav}

    <div class="sidebar-footer">
      <a href="{instagram}" target="_blank" rel="noopener">Instagram</a>
      <a href="mailto:{email}">{email}</a>
    </div>
  </div>
</aside>

<main id="main-content" class="main-content">
  {main_content}
</main>

<div id="lightbox" class="lightbox" hidden>
  <button class="lightbox-close" aria-label="Close">&times;</button>
  <button class="lightbox-prev" aria-label="Previous">&#8249;</button>
  <img class="lightbox-img" src="" alt="">
  <button class="lightbox-next" aria-label="Next">&#8250;</button>
</div>

<script>window.PAGE = {page_json};</script>
<script src="{asset_prefix}js/data.js"></script>
<script src="{asset_prefix}js/app.js"></script>
</body>
</html>
"""


def render_image(file, alt, w, h, depth):
    prefix = "../" if depth else ""
    dims = ' width="{}" height="{}"'.format(w, h) if w and h else ""
    return '<img src="{prefix}images/{file}" alt="{alt}"{dims} loading="lazy">'.format(
        prefix=prefix, file=file, alt=html_escape(alt), dims=dims
    )


def render_grid(images, depth):
    items = "\n    ".join(
        render_image(img["file"], img["alt"], img.get("w"), img.get("h"), depth) for img in images
    )
    return '<div class="grid" id="photo-grid">\n    {}\n  </div>'.format(items)


def render_about(data, depth):
    prefix = "../" if depth else ""
    about = data["about"]
    email = data["site"]["email"]

    photo_html = '<img class="about-photo" src="{prefix}images/{photo}" alt="Skyler Hughes">'.format(
        prefix=prefix, photo=about["photo"]
    )

    paragraph_htmls = []
    for text in about["paragraphs"]:
        if email in text:
            before, after = text.split(email, 1)
            paragraph_htmls.append(
                '<p>{before}<a href="mailto:{email}">{email}</a>{after}</p>'.format(
                    before=html_escape(before), email=html_escape(email), after=html_escape(after)
                )
            )
        else:
            paragraph_htmls.append("<p>{}</p>".format(html_escape(text)))

    return '<div class="about-page">\n    {photo}\n    <h1>About</h1>\n    {paragraphs}\n  </div>'.format(
        photo=photo_html, paragraphs="\n    ".join(paragraph_htmls)
    )


def write_page(rel_dir, title, description, canonical_slug, og_image, page_json, nav_html, main_content=""):
    depth = 1 if rel_dir else 0
    page_json = dict(page_json, depth=depth)
    head = render_head(title, description, canonical_slug, og_image, depth)
    asset_prefix = "../" if depth else ""
    html = PAGE_SHELL.format(
        head=head,
        nav=nav_html,
        instagram=SITE_DATA_SITE["instagram"],
        email=SITE_DATA_SITE["email"],
        main_content=main_content,
        page_json=json.dumps(page_json),
        asset_prefix=asset_prefix,
    )
    out_dir = os.path.join(BASE, rel_dir) if rel_dir else BASE
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w") as f:
        f.write(html)


def main():
    global SITE_DATA_SITE
    data = load_data()
    SITE_DATA_SITE = data["site"]
    pages = page_list(data)
    tagline = data["site"]["tagline"]

    # Home
    home_desc = tagline
    home_og_image = "images/" + data["home"][0]["file"]
    nav_html = render_nav(data, pages, "home", depth=0)
    home_content = (
        '<h1 class="sr-only">Skyler Hughes Photography</h1>\n'
        '  <div class="home-intro"><p>{}</p></div>\n'
        '  {}'
    ).format(html_escape(tagline), render_grid(data["home"], depth=0))
    write_page(
        "", "Skyler Hughes Photography", home_desc, "", home_og_image,
        {"type": "home"}, nav_html, home_content,
    )

    # Galleries
    for item in data["nav"]:
        gid, label = item["id"], item["label"]
        images = data["galleries"][gid]
        title = "{} Photography | Skyler Hughes".format(label)
        description = "{} landscape and outdoor photography by Skyler Hughes. Browse the full {} gallery.".format(
            label, label
        )
        og_image = "images/" + images[0]["file"]
        nav_html = render_nav(data, pages, gid, depth=1)
        main_content = '<h1 class="page-title">{}</h1>\n  {}'.format(
            html_escape(label), render_grid(images, depth=1)
        )
        write_page(
            gid, title, description, gid + "/", og_image,
            {"type": "gallery", "id": gid}, nav_html, main_content,
        )

    # About
    about_title = "About | Skyler Hughes Photography"
    about_desc = data["about"]["paragraphs"][0][:155].rsplit(" ", 1)[0] + "…"
    about_og_image = "images/" + data["about"]["photo"]
    nav_html = render_nav(data, pages, "about", depth=1)
    about_content = render_about(data, depth=1)
    write_page(
        "about", about_title, about_desc, "about/", about_og_image,
        {"type": "about"}, nav_html, about_content,
    )

    # sitemap.xml + robots.txt
    urls = [SITE_BASE_URL] + [SITE_BASE_URL + p["slug"] for p in pages if p["slug"]]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append("  <url><loc>{}</loc></url>".format(u))
    sitemap.append("</urlset>")
    with open(os.path.join(BASE, "sitemap.xml"), "w") as f:
        f.write("\n".join(sitemap) + "\n")

    with open(os.path.join(BASE, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: {}sitemap.xml\n".format(SITE_BASE_URL))

    print("Generated {} pages + sitemap.xml + robots.txt".format(len(pages)))


if __name__ == "__main__":
    main()
