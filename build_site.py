#!/usr/bin/env python3
"""Generates the static HTML pages (index.html, /central-oregon/index.html, ...)
from js/data.js. Re-run this after editing js/data.js (new photos, new gallery,
changed bio, etc.) to keep every page's nav/meta in sync.
"""

import json
import os
from datetime import date

BASE = os.path.dirname(os.path.abspath(__file__))
SITE_BASE_URL = "https://skylerhughesphotography.com/"


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


def format_date(iso_date):
    return date.fromisoformat(iso_date).strftime("%B {}, %Y").format(
        date.fromisoformat(iso_date).day
    )


def sorted_posts(data):
    return sorted(data.get("blog", []), key=lambda p: p["date"], reverse=True)


def render_nav(data, pages, active_id, depth):
    prefix = "../" * depth
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

    blog_active = " active" if active_id == "blog" else ""
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
        <li><a href="{blog_href}" class="nav-link{blog_active}">Blog</a></li>
        <li><a href="{about_href}" class="nav-link{about_active}">About</a></li>
      </ul>
    </nav>""".format(
        home_href=prefix if prefix else "./",
        gallery_lis="\n          ".join(gallery_lis),
        blog_href=prefix + "blog/",
        blog_active=blog_active,
        about_href=prefix + "about/",
        about_active=about_active,
    )


def render_head(title, description, canonical_slug, og_image_path, depth, structured_data=""):
    asset_prefix = "../" * depth
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


def render_image(file, alt, w, h, depth, loading="lazy", fetchpriority=None, css_class=None):
    prefix = "../" * depth
    dims = ' width="{}" height="{}"'.format(w, h) if w and h else ""
    priority = ' fetchpriority="{}"'.format(fetchpriority) if fetchpriority else ""
    cls = ' class="{}"'.format(css_class) if css_class else ""
    return '<img src="{prefix}images/{file}" alt="{alt}"{cls}{dims} loading="{loading}"{priority}>'.format(
        prefix=prefix, file=file, alt=html_escape(alt), cls=cls, dims=dims, loading=loading, priority=priority
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
    prefix = "../" * depth
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


def render_blog_index(posts, depth):
    prefix = "../" * depth
    if not posts:
        return (
            '<h1 class="page-title">Blog</h1>\n'
            '  <div class="home-intro"><p>No posts yet -- check back soon.</p></div>'
        )

    item_htmls = []
    for post in posts:
        cover_html = ""
        if post.get("cover"):
            cover_html = '<img class="blog-item-cover" src="{prefix}images/{cover}" alt="" loading="lazy">'.format(
                prefix=prefix, cover=post["cover"]
            )
        item_htmls.append(
            '<a class="blog-item" href="{prefix}blog/{slug}/">\n'
            "      {cover}\n"
            '      <div class="blog-item-body">\n'
            '        <h2 class="blog-item-title">{title}</h2>\n'
            '        <div class="blog-item-meta">{date}</div>\n'
            '        <p class="blog-item-excerpt">{excerpt}</p>\n'
            "      </div>\n"
            "    </a>".format(
                prefix=prefix,
                slug=post["slug"],
                cover=cover_html,
                title=html_escape(post["title"]),
                date=format_date(post["date"]),
                excerpt=html_escape(post["excerpt"]),
            )
        )

    return '<h1 class="page-title">Blog</h1>\n  <div class="blog-list">\n    {}\n  </div>'.format(
        "\n    ".join(item_htmls)
    )


def render_day_section(day, depth):
    photos = day.get("photos", [])
    hero_idx = next(
        (i for i, p in enumerate(photos) if p.get("w") and p.get("h") and p["w"] >= p["h"]),
        0 if photos else None,
    )
    hero = photos[hero_idx] if hero_idx is not None else None
    rest = [(i, p) for i, p in enumerate(photos) if i != hero_idx]

    hero_html = ""
    if hero:
        hero_html = render_image(
            hero["file"], hero.get("alt") or "{} -- photo {}".format(day["title"], hero_idx + 1),
            hero.get("w"), hero.get("h"), depth, css_class="day-hero",
        ) + "\n      "

    grid_html = ""
    if rest:
        photos_html = "\n        ".join(
            render_image(
                p["file"],
                p.get("alt") or "{} -- photo {}".format(day["title"], orig_i + 1),
                p.get("w"), p.get("h"), depth,
            )
            for orig_i, p in rest
        )
        grid_html = (
            '<div class="day-photos">\n'
            "        {photos}\n"
            "      </div>\n"
        ).format(photos=photos_html)

    text_html = "<p>{}</p>\n      ".format(html_escape(day["text"])) if day.get("text") else ""
    return (
        '<div class="day-section">\n'
        "      <h2>{title}</h2>\n"
        "      {text}"
        "{hero}"
        "{grid}"
        "    </div>"
    ).format(title=html_escape(day["title"]), text=text_html, hero=hero_html, grid=grid_html)


def render_blog_post(post, depth):
    prefix = "../" * depth
    cover_html = ""
    if post.get("cover"):
        cover_html = '<img class="blog-post-cover" src="{prefix}images/{cover}" alt="">\n    '.format(
            prefix=prefix, cover=post["cover"]
        )

    paragraph_htmls = "\n    ".join(
        "<p>{}</p>".format(html_escape(text)) for text in post.get("paragraphs", [])
    )

    days_html = ""
    if post.get("days"):
        days_html = "\n    ".join(render_day_section(day, depth) for day in post["days"])

    wrapper_class = "blog-post blog-post--essay" if post.get("days") else "blog-post"

    return (
        '<div class="{wrapper_class}">\n'
        "    {cover}"
        "<h1>{title}</h1>\n"
        '    <div class="blog-post-meta">{date}</div>\n'
        "    {paragraphs}\n"
        "    {days}\n"
        "  </div>"
    ).format(
        wrapper_class=wrapper_class,
        cover=cover_html,
        title=html_escape(post["title"]),
        date=format_date(post["date"]),
        paragraphs=paragraph_htmls,
        days=days_html,
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


def blog_posting_jsonld(post):
    url = SITE_BASE_URL + "blog/" + post["slug"] + "/"
    obj = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "description": post["excerpt"],
        "url": url,
        "datePublished": post["date"],
        "author": {"@type": "Person", "name": "Skyler Hughes", "url": SITE_BASE_URL},
    }
    if post.get("cover"):
        obj["image"] = SITE_BASE_URL + "images/" + post["cover"]
    return obj


def write_page(rel_dir, title, description, canonical_slug, og_image, page_json, nav_html, main_content="", structured_data=""):
    depth = rel_dir.count("/") + 1 if rel_dir else 0
    page_json = dict(page_json, depth=depth)
    head = render_head(title, description, canonical_slug, og_image, depth, structured_data)
    asset_prefix = "../" * depth
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
        <li><a href="{blog}" class="nav-link">Blog</a></li>
        <li><a href="{about}" class="nav-link">About</a></li>
      </ul>
    </nav>""".format(
        home=SITE_BASE_URL,
        items="\n          ".join(nav_lis),
        blog=SITE_BASE_URL + "blog/",
        about=SITE_BASE_URL + "about/",
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
    build_date = date.today().isoformat()

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
    sitemap_entries = [(SITE_BASE_URL, data["home"], build_date)]

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
        sitemap_entries.append((SITE_BASE_URL + gid + "/", images, build_date))

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
    sitemap_entries.append(
        (SITE_BASE_URL + "about/", [{"file": data["about"]["photo"], "alt": "Skyler Hughes"}], build_date)
    )

    # Blog
    posts = sorted_posts(data)
    blog_title = "Blog | Skyler Hughes Photography"
    blog_desc = "Notes on locations, technique, and gear from Skyler Hughes."
    blog_og_image = "images/" + posts[0]["cover"] if posts and posts[0].get("cover") else home_og_image
    nav_html = render_nav(data, pages, "blog", depth=1)
    blog_content = render_blog_index(posts, depth=1)
    blog_structured_data = render_jsonld({
        "@context": "https://schema.org",
        "@type": "Blog",
        "name": "Skyler Hughes Photography Blog",
        "url": SITE_BASE_URL + "blog/",
        "blogPost": [blog_posting_jsonld(post) for post in posts],
    })
    write_page(
        "blog", blog_title, blog_desc, "blog/", blog_og_image,
        {"type": "blog"}, nav_html, blog_content, blog_structured_data,
    )
    blog_index_images = [
        {"file": post["cover"], "alt": post["title"]} for post in posts if post.get("cover")
    ]
    sitemap_entries.append((SITE_BASE_URL + "blog/", blog_index_images, build_date))

    for post in posts:
        post_title = "{} | Skyler Hughes Photography".format(post["title"])
        post_slug = "blog/" + post["slug"]
        post_og_image = "images/" + post["cover"] if post.get("cover") else home_og_image
        nav_html = render_nav(data, pages, "blog", depth=2)
        post_content = render_blog_post(post, depth=2)
        post_structured_data = render_jsonld(blog_posting_jsonld(post))
        write_page(
            post_slug, post_title, post["excerpt"], post_slug + "/", post_og_image,
            {"type": "blog-post", "slug": post["slug"]}, nav_html, post_content, post_structured_data,
        )
        post_images = [{"file": post["cover"], "alt": post["title"]}] if post.get("cover") else []
        sitemap_entries.append((SITE_BASE_URL + post_slug + "/", post_images, post["date"]))

    # sitemap.xml (with the image sitemap extension, since this is a photo site
    # and captioned image entries are a direct lever for Google Images traffic)
    # + robots.txt
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">',
    ]
    for url, images, lastmod in sitemap_entries:
        sitemap.append("  <url>")
        sitemap.append("    <loc>{}</loc>".format(url))
        sitemap.append("    <lastmod>{}</lastmod>".format(lastmod))
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

    total_pages = len(pages) + 1 + len(posts)
    print("Generated {} pages + 404.html + sitemap.xml + robots.txt".format(total_pages))


if __name__ == "__main__":
    main()
