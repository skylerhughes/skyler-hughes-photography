#!/usr/bin/env python3
"""Generates the static HTML pages (index.html, /central-oregon/index.html, ...)
from js/data.js. Re-run this after editing js/data.js (new photos, new gallery,
changed bio, etc.) to keep every page's nav/meta in sync.
"""

import json
import os
from datetime import date

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


def render_head(title, description, canonical_slug, og_image_path, depth, structured_data=""):
    asset_prefix = "../" if depth else ""
    canonical_url = SITE_BASE_URL + canonical_slug
    og_image_url = SITE_BASE_URL + og_image_path
    return """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical_url}">
<link rel="icon" type="image/svg+xml" href="{asset_prefix}favicon.svg">

<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical_url}">
<meta property="og:image" content="{og_image_url}">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image_url}">

<link rel="stylesheet" href="{asset_prefix}css/style.css">
{structured_data}""".format(
        title=html_escape(title),
        description=html_escape(description),
        canonical_url=canonical_url,
        og_image_url=og_image_url,
        asset_prefix=asset_prefix,
        structured_data=structured_data,
    ).rstrip()


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


def render_image(file, alt, w, h, depth, loading="lazy", fetchpriority=None):
    prefix = "../" if depth else ""
    dims = ' width="{}" height="{}"'.format(w, h) if w and h else ""
    priority = ' fetchpriority="{}"'.format(fetchpriority) if fetchpriority else ""
    return '<img src="{prefix}images/{file}" alt="{alt}"{dims} loading="{loading}"{priority}>'.format(
        prefix=prefix, file=file, alt=html_escape(alt), dims=dims, loading=loading, priority=priority
    )


def render_grid(images, depth):
    items = []
    for i, img in enumerate(images):
        if i == 0:
            loading, fetchpriority = "eager", "high"
        elif i == 1:
            loading, fetchpriority = "eager", None
        else:
            loading, fetchpriority = "lazy", None
        items.append(
            render_image(img["file"], img["alt"], img.get("w"), img.get("h"), depth, loading, fetchpriority)
        )
    return '<div class="grid" id="photo-grid">\n    {}\n  </div>'.format("\n    ".join(items))


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


def render_jsonld(obj):
    return '<script type="application/ld+json">{}</script>'.format(json.dumps(obj))


def person_jsonld(data):
    site = data["site"]
    return {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": "Skyler Hughes",
        "url": SITE_BASE_URL,
        "image": SITE_BASE_URL + "images/" + data["about"]["photo"],
        "email": site["email"],
        "jobTitle": "Photographer",
        "sameAs": [site["instagram"]],
    }


def image_gallery_jsonld(name, url, images):
    return {
        "@context": "https://schema.org",
        "@type": "ImageGallery",
        "name": name,
        "url": url,
        "image": [
            {
                "@type": "ImageObject",
                "contentUrl": SITE_BASE_URL + "images/" + img["file"],
                "name": img["alt"],
            }
            for img in images
        ],
    }


def write_page(rel_dir, title, description, canonical_slug, og_image, page_json, nav_html, main_content="", structured_data=""):
    depth = 1 if rel_dir else 0
    page_json = dict(page_json, depth=depth)
    head = render_head(title, description, canonical_slug, og_image, depth, structured_data)
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


def write_404_page(data):
    # GitHub Pages serves this for any unmatched path, but the browser's address
    # bar still shows that (nonexistent) path, so every asset/nav reference here
    # must be a fully-qualified absolute URL rather than a relative one -- a
    # relative "../css/style.css" would resolve against whatever depth the
    # mistyped URL happened to be at, not against this file's own location.
    nav_lis = []
    for item in data["nav"]:
        nav_lis.append(
            '<li><a href="{}{}/" class="nav-link">{}</a></li>'.format(
                SITE_BASE_URL, item["id"], html_escape(item["label"])
            )
        )
    nav_html = """
<a href="{home}" class="site-name">Skyler<br>Hughes</a>

    <nav class="site-nav" aria-label="Primary">
      <div class="nav-group">
        <span class="nav-group-label">Image Galleries</span>
        <ul>
          {items}
        </ul>
      </div>
      <ul class="nav-flat">
        <li><a href="{about}" class="nav-link">About</a></li>
      </ul>
    </nav>""".format(
        home=SITE_BASE_URL, items="\n          ".join(nav_lis), about=SITE_BASE_URL + "about/"
    )

    main_content = (
        '<h1 class="page-title">Page not found</h1>\n'
        '  <div class="home-intro"><p>The page you\'re looking for doesn\'t exist. '
        'Head back to the <a href="{home}">homepage</a> or pick a gallery from the nav.</p></div>'
    ).format(home=SITE_BASE_URL)

    site = data["site"]
    html = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Page Not Found | Skyler Hughes Photography</title>
<meta name="robots" content="noindex">
<link rel="icon" type="image/svg+xml" href="{favicon}">
<link rel="stylesheet" href="{css}">
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

<script>
  document.getElementById("nav-toggle").addEventListener("click", function () {{
    var open = document.getElementById("sidebar").classList.toggle("open");
    this.setAttribute("aria-expanded", String(open));
  }});
</script>
</body>
</html>
""".format(
        favicon=SITE_BASE_URL + "favicon.svg",
        css=SITE_BASE_URL + "css/style.css",
        nav=nav_html,
        instagram=site["instagram"],
        email=site["email"],
        main_content=main_content,
    )

    with open(os.path.join(BASE, "404.html"), "w") as f:
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
    home_structured_data = "\n".join([
        render_jsonld(person_jsonld(data)),
        render_jsonld(image_gallery_jsonld("Skyler Hughes Photography", SITE_BASE_URL, data["home"])),
    ])
    write_page(
        "", "Skyler Hughes Photography", home_desc, "", home_og_image,
        {"type": "home"}, nav_html, home_content, home_structured_data,
    )
    sitemap_entries = [(SITE_BASE_URL, data["home"])]

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
        gallery_structured_data = render_jsonld(
            image_gallery_jsonld(
                "{} Photography | Skyler Hughes".format(label), SITE_BASE_URL + gid + "/", images
            )
        )
        write_page(
            gid, title, description, gid + "/", og_image,
            {"type": "gallery", "id": gid}, nav_html, main_content, gallery_structured_data,
        )
        sitemap_entries.append((SITE_BASE_URL + gid + "/", images))

    # About
    about_title = "About | Skyler Hughes Photography"
    about_desc = data["about"]["paragraphs"][0][:155].rsplit(" ", 1)[0] + "…"
    about_og_image = "images/" + data["about"]["photo"]
    nav_html = render_nav(data, pages, "about", depth=1)
    about_content = render_about(data, depth=1)
    about_structured_data = render_jsonld(person_jsonld(data))
    write_page(
        "about", about_title, about_desc, "about/", about_og_image,
        {"type": "about"}, nav_html, about_content, about_structured_data,
    )
    sitemap_entries.append((SITE_BASE_URL + "about/", [{"file": data["about"]["photo"], "alt": "Skyler Hughes"}]))

    # sitemap.xml (with the image sitemap extension, since this is a photo site
    # and captioned image entries are a direct lever for Google Images traffic)
    # + robots.txt
    build_date = date.today().isoformat()
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for url, images in sitemap_entries:
        sitemap.append("  <url>")
        sitemap.append("    <loc>{}</loc>".format(url))
        sitemap.append("    <lastmod>{}</lastmod>".format(build_date))
        for img in images:
            sitemap.append("    <image:image>")
            sitemap.append("      <image:loc>{}images/{}</image:loc>".format(SITE_BASE_URL, img["file"]))
            sitemap.append("      <image:caption>{}</image:caption>".format(html_escape(img["alt"])))
            sitemap.append("    </image:image>")
        sitemap.append("  </url>")
    sitemap.append("</urlset>")
    with open(os.path.join(BASE, "sitemap.xml"), "w") as f:
        f.write("\n".join(sitemap) + "\n")

    with open(os.path.join(BASE, "robots.txt"), "w") as f:
        f.write("User-agent: *\nAllow: /\n\nSitemap: {}sitemap.xml\n".format(SITE_BASE_URL))

    write_404_page(data)

    print("Generated {} pages + 404.html + sitemap.xml + robots.txt".format(len(pages)))


if __name__ == "__main__":
    main()
