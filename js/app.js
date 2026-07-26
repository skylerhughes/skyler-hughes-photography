(function () {
  "use strict";

  const main = document.getElementById("main-content");
  const galleryNavList = document.getElementById("gallery-nav-list");
  const sidebar = document.getElementById("sidebar");
  const navToggle = document.getElementById("nav-toggle");

  const lightbox = document.getElementById("lightbox");
  const lightboxImg = lightbox.querySelector(".lightbox-img");
  let currentImages = [];
  let currentIndex = 0;

  function imgSrc(file) {
    return "images/" + file;
  }

  // Build sidebar gallery links from data
  SITE_DATA.nav.forEach(function (item) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = "#" + item.id;
    a.textContent = item.label;
    a.dataset.nav = item.id;
    li.appendChild(a);
    galleryNavList.appendChild(li);
  });

  document.getElementById("instagram-link").href = SITE_DATA.site.instagram;
  document.getElementById("email-link").href = "mailto:" + SITE_DATA.site.email;
  document.getElementById("email-link").textContent = SITE_DATA.site.email;

  function setActiveNav(id) {
    document.querySelectorAll(".site-nav a").forEach(function (a) {
      a.classList.toggle("active", a.dataset.nav === id);
    });
  }

  const GAP = 6;

  function targetRowHeight() {
    return window.innerWidth <= 860 ? 220 : 380;
  }

  function layoutRows(container, images, rowHeight) {
    const containerWidth = container.clientWidth;
    let row = [];
    let rowAspectSum = 0;

    function flushRow(isLastRow) {
      if (!row.length) return;
      const rowGaps = GAP * (row.length - 1);
      const naturalWidth = rowAspectSum * rowHeight + rowGaps;
      const fill = !isLastRow || naturalWidth > containerWidth;

      const rowEl = document.createElement("div");
      rowEl.className = "grid-row" + (fill ? " grid-row--fill" : "");

      row.forEach(function (entry) {
        const cell = document.createElement("div");
        cell.className = "grid-item";
        cell.style.setProperty("--row-height", rowHeight + "px");
        if (fill) {
          cell.style.flexGrow = String(entry.aspect);
        } else {
          cell.style.width = (entry.aspect * rowHeight) + "px";
        }
        const img = document.createElement("img");
        img.src = imgSrc(entry.item.file);
        img.alt = entry.item.alt;
        img.loading = "lazy";
        cell.appendChild(img);
        cell.addEventListener("click", function () {
          openLightbox(images, entry.index);
        });
        rowEl.appendChild(cell);
      });

      container.appendChild(rowEl);
      row = [];
      rowAspectSum = 0;
    }

    images.forEach(function (item, index) {
      const aspect = (item.w && item.h) ? item.w / item.h : 4 / 3;
      row.push({ item: item, index: index, aspect: aspect });
      rowAspectSum += aspect;
      const rowGaps = GAP * (row.length - 1);
      const widthAtTarget = rowAspectSum * rowHeight + rowGaps;
      if (widthAtTarget >= containerWidth) {
        flushRow(false);
      }
    });
    flushRow(true);
  }

  function renderGrid(images) {
    const grid = document.createElement("div");
    grid.className = "grid";
    // Deferred layout: container needs to be attached to measure width.
    requestAnimationFrame(function () {
      layoutRows(grid, images, targetRowHeight());
    });

    let resizeTimer = null;
    const onResize = function () {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(function () {
        if (!grid.isConnected) {
          window.removeEventListener("resize", onResize);
          return;
        }
        grid.innerHTML = "";
        layoutRows(grid, images, targetRowHeight());
      }, 150);
    };
    window.addEventListener("resize", onResize);

    return grid;
  }

  function renderHome() {
    main.innerHTML = "";
    main.appendChild(renderGrid(SITE_DATA.home));
    setActiveNav(null);
  }

  function renderGallery(id) {
    const images = SITE_DATA.galleries[id];
    const label = (SITE_DATA.nav.find(function (n) { return n.id === id; }) || {}).label || id;
    main.innerHTML = "";
    const title = document.createElement("h2");
    title.className = "page-title";
    title.textContent = label;
    main.appendChild(title);
    main.appendChild(renderGrid(images));
    setActiveNav(id);
  }

  function renderAbout() {
    main.innerHTML = "";
    const wrap = document.createElement("div");
    wrap.className = "about-page";

    const photo = document.createElement("img");
    photo.className = "about-photo";
    photo.src = imgSrc(SITE_DATA.about.photo);
    photo.alt = "Skyler Hughes";
    wrap.appendChild(photo);

    const h1 = document.createElement("h1");
    h1.textContent = "About";
    wrap.appendChild(h1);

    SITE_DATA.about.paragraphs.forEach(function (text) {
      const p = document.createElement("p");
      const parts = text.split(SITE_DATA.site.email);
      if (parts.length === 2) {
        p.appendChild(document.createTextNode(parts[0]));
        const a = document.createElement("a");
        a.href = "mailto:" + SITE_DATA.site.email;
        a.textContent = SITE_DATA.site.email;
        p.appendChild(a);
        p.appendChild(document.createTextNode(parts[1]));
      } else {
        p.textContent = text;
      }
      wrap.appendChild(p);
    });

    main.appendChild(wrap);
    setActiveNav("about");
  }

  function route() {
    const hash = window.location.hash.replace(/^#/, "") || "home";
    closeLightbox();
    if (hash === "home") {
      renderHome();
    } else if (hash === "about") {
      renderAbout();
    } else if (SITE_DATA.galleries[hash]) {
      renderGallery(hash);
    } else {
      renderHome();
    }
    window.scrollTo(0, 0);
    closeSidebarOnMobile();
  }

  // ---------- Lightbox ----------

  function openLightbox(images, index) {
    currentImages = images;
    currentIndex = index;
    showCurrentImage();
    lightbox.hidden = false;
  }

  function showCurrentImage() {
    const item = currentImages[currentIndex];
    lightboxImg.src = imgSrc(item.file);
    lightboxImg.alt = item.alt;
  }

  function closeLightbox() {
    lightbox.hidden = true;
    lightboxImg.src = "";
  }

  function showNext(delta) {
    if (!currentImages.length) return;
    currentIndex = (currentIndex + delta + currentImages.length) % currentImages.length;
    showCurrentImage();
  }

  lightbox.querySelector(".lightbox-close").addEventListener("click", closeLightbox);
  lightbox.querySelector(".lightbox-prev").addEventListener("click", function () { showNext(-1); });
  lightbox.querySelector(".lightbox-next").addEventListener("click", function () { showNext(1); });
  lightbox.addEventListener("click", function (e) {
    if (e.target === lightbox) closeLightbox();
  });

  document.addEventListener("keydown", function (e) {
    if (lightbox.hidden) return;
    if (e.key === "Escape") closeLightbox();
    if (e.key === "ArrowLeft") showNext(-1);
    if (e.key === "ArrowRight") showNext(1);
  });

  // ---------- Mobile nav ----------

  function closeSidebarOnMobile() {
    sidebar.classList.remove("open");
    navToggle.setAttribute("aria-expanded", "false");
  }

  navToggle.addEventListener("click", function () {
    const open = sidebar.classList.toggle("open");
    navToggle.setAttribute("aria-expanded", String(open));
  });

  window.addEventListener("hashchange", route);
  document.addEventListener("DOMContentLoaded", route);
  route();
})();
